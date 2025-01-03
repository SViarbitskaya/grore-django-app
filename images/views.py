from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic, View
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.utils import translation
from django.template.loader import render_to_string
import json, re, random, zipfile, os
import logging

from .models import Image
from .forms import ImageSearchForm
from .mixins import SelectionMixin

class HomeView(SelectionMixin, generic.ListView):
    model = Image
    template_name = "images/index.html"
    context_object_name = "images"
    paginate_by = 15

    def get_template_names(self, *args, **kwargs):
        if self.request.htmx:
            return "images/htmx_partial.html"
        else:
            return self.template_name

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search_query')
        
        if search_query:
            search_terms = search_query.split()
            
            # Create a regex pattern that matches whole words with optional punctuation
            def contains_full_word(note):
                for term in search_terms:
                    pattern = fr'\b{re.escape(term)}\b[\s.,;:!?]*'
                    if re.search(pattern, note, re.IGNORECASE):
                        return True
                return False
            
            # Filter the queryset based on the presence of full words
            queryset = queryset.filter(note__in=[note.note for note in queryset if contains_full_word(note.note)])
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
            logger.info(image.file.path)
            if os.path.exists(image.file.path):
                # Add the image to the zip file
                zip_file.write(image.file.path, arcname=os.path.basename(image.file.path))

    return response

class ToggleSelectionView(SelectionMixin, View):
    def post(self, request, *args, **kwargs):
        return JsonResponse(self.update_session_selection(request))
