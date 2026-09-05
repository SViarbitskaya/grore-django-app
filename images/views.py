from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic, View
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.utils import translation
from django.template.loader import render_to_string
from pgvector.django import CosineDistance
import json, re, random, zipfile, os
import logging

from .models import Image
from .forms import ImageSearchForm
from .mixins import SelectionMixin
from .embeddings import embed_text
from .stopwords import filter_stopwords, stopwords_for_language

# Cosine distance ranges 0 (identical) to 2 (opposite); notules beyond this
# are treated as irrelevant rather than returned as low-quality matches.
# 0.5 was measured to be too strict for this model on this corpus: even for
# a query like "human" against hundreds of genuinely matching man/woman
# portrait captions, the single closest match in the whole DB sat at 0.509 --
# just above the old cutoff -- so almost nothing came back. 0.6 was checked
# against several queries (roughly doubles the relevant results returned for
# common nouns) without admitting noise for concepts absent from the corpus
# (e.g. "submarine"/"volcano" still only surface sensible near-analogies:
# boats, mountains -- not random captions).
SEMANTIC_SEARCH_MAX_DISTANCE = 0.6

class HomeView(SelectionMixin, generic.ListView):
    model = Image
    template_name = "images/index.html"
    context_object_name = "images"
    paginate_by = 10

    def get_template_names(self, *args, **kwargs):
        if self.request.htmx:
            return "images/htmx_partial.html"
        else:
            return self.template_name

    def get_queryset(self):
        # Deferred: browsing/exact-match never reads the raw vectors, and
        # fetching+deserializing two 384-dim floats per row for ~3k rows
        # on every homepage load was adding real latency. The semantic
        # query below still works deferred, since CosineDistance references
        # the column at the SQL level, not through the Python attribute.
        queryset = super().get_queryset().defer('note_en_embedding', 'note_fr_embedding')
        search_query = self.request.GET.get('search_query')

        if search_query:
            # Stopwords (bilingual EN/FR) are dropped before matching: common
            # function words like "a"/"and"/"le"/"et" appear in nearly every
            # notule, so leaving them in makes exact-match match everything
            # and pollutes the semantic query embedding.
            search_terms = filter_stopwords(
                search_query.split(), stopwords_for_language(self.request.LANGUAGE_CODE)
            )

            if not search_terms:
                # Query was only stopwords (e.g. "a", "and the") -- not a
                # meaningful search term, so fall back to the browse view
                # instead of matching either everything or nothing.
                queryset = list(queryset)
                random.shuffle(queryset)
                return queryset

            # Create a regex pattern that matches whole words with optional
            # punctuation. All terms must match (AND), not just one (OR) --
            # otherwise a multi-word query matches on any single word alone.
            def contains_full_word(note):
                for term in search_terms:
                    pattern = fr'\b{re.escape(term)}\b[\s.,;:!?]*'
                    if not re.search(pattern, note, re.IGNORECASE):
                        return False
                return True

            # Exact whole-word matches are ranked first. Ordered by pk so the
            # result order is stable across the separate paginated requests
            # HTMX infinite scroll makes for page 2, 3, ... (Image has no
            # default ordering, so without this the same row can land on
            # more than one page and show up as a duplicate).
            exact_matches = [
                image for image in queryset.order_by('pk') if contains_full_word(image.note)
            ]
            exact_match_ids = {image.id for image in exact_matches}

            # Semantic matches fill in the rest, ranked by similarity. 'pk'
            # is a tiebreaker for the same pagination-stability reason.
            embedding_field = (
                'note_en_embedding' if self.request.LANGUAGE_CODE == 'en' else 'note_fr_embedding'
            )
            query_vector = embed_text(' '.join(search_terms))
            semantic_matches = list(
                queryset.exclude(id__in=exact_match_ids)
                .filter(**{f'{embedding_field}__isnull': False})
                .annotate(distance=CosineDistance(embedding_field, query_vector))
                .filter(distance__lt=SEMANTIC_SEARCH_MAX_DISTANCE)
                .order_by('distance', 'pk')
            )

            queryset = exact_matches + semantic_matches
        else:
            # Shuffle the queryset if no search query is present
            queryset = list(queryset)
            random.shuffle(queryset)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = ImageSearchForm(self.request.GET)
        context['language'] = self.request.LANGUAGE_CODE
        context['redirect_to'] = self.request.path
        # Convert stored IDs in the session to integers
        selected_images = self.request.session.get('selected_images', [])

        # Safely convert to integers, catching any invalid data
        selected_images_ids = []

        for item in selected_images:
            try:
                if item is not None:  # Make sure item is not None
                    selected_images_ids.append(int(item))
            except (ValueError, TypeError):  # Handle any conversion issues
                pass  # Skip invalid items, optionally log them

        context['selected_images_ids'] = selected_images_ids
        page_number = self.request.GET.get('page', 1)
        context['calculated_height'] = 100 * int(page_number)
        return context


class SelectionView(SelectionMixin, View):
    template_name = "images/selection.html"

    def get(self, request, *args, **kwargs):
        # Use the mixin to get the selected images
        images = self.get_selected_images(request)
        return render(request, self.template_name, {'images': images})

    def delete(self, request, *args, **kwargs):
        # Handle image deletion
        image_id = str(kwargs.get('image_id'))
        selected_images = request.session.get('selected_images', [])

        if image_id in selected_images:
            selected_images.remove(image_id)
            request.session['selected_images'] = selected_images
            # Check if any images are left in the selection
            if not selected_images:
                # If no images left, return just the translated "No images selected." message
                no_images_message = render_to_string("images/no_images.html")
                return HttpResponse(no_images_message, content_type="text/html", status=200)
            return HttpResponse("", status=200)

        return HttpResponse(status=400)


class ClearSelectionView(SelectionMixin, View):
    def delete(self, request, *args, **kwargs):
        # Empty the whole selection in one go rather than removing images
        # one at a time -- the session holds the selection, not a DB table,
        # so this is just resetting that list.
        request.session['selected_images'] = []
        no_images_message = render_to_string("images/no_images.html")
        return HttpResponse(no_images_message, content_type="text/html", status=200)


class ToggleSelectionView(SelectionMixin, View):
    def post(self, request, *args, **kwargs):
        return JsonResponse(self.update_session_selection(request))


def download_images(request):
    # Get the list of image IDs from the session
    selected_image_ids = request.session.get('selected_images', [])
    
    # Fetch the images from the database
    images = Image.objects.filter(id__in=selected_image_ids)

    # Create a zip file in memory
    zip_filename = "selected_images.zip"
    response = HttpResponse(content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename={zip_filename}'

    logger = logging.getLogger(__name__)

    with zipfile.ZipFile(response, 'w') as zip_file:
        for image in images:
            # Ensure the image file exists

            if image.file and os.path.exists(image.file.path):
                # Add the image to the zip file
                zip_file.write(
                    image.file.path, 
                    arcname=os.path.basename(image.file.path)
                )

            # Add low-res thumbnail if it exists
            if image.thumbnail and os.path.exists(image.thumbnail.path):
                zip_file.write(
                    image.thumbnail.path,
                    arcname=os.path.basename(image.thumbnail.path)
                )

    return response

def download_zip(request, image_id):
    # Fetch the image
    image = get_object_or_404(Image, pk=image_id)

    # Name of the zip file
    zip_filename = f"{image.identifier}.zip"
    # Create the response
    response = HttpResponse(content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{zip_filename}"'

    logger = logging.getLogger(__name__)

    with zipfile.ZipFile(response, 'w') as zip_file:
        # Add high-res file if it exists
        if image.file and os.path.exists(image.file.path):
            zip_file.write(
                image.file.path,
                arcname=os.path.basename(image.file.path)
            )
        # Add low-res thumbnail if it exists
        if image.thumbnail and os.path.exists(image.thumbnail.path):
            zip_file.write(
                image.thumbnail.path,
                arcname=os.path.basename(image.thumbnail.path)
            )

    return response
