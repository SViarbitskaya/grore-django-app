from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic, View
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.utils import translation
import json

from .models import Image
from .forms import ImageSearchForm
from .mixins import SelectionMixin

class HomeView(SelectionMixin, generic.ListView):
    model = Image
    template_name = "images/index.html"
    context_object_name = "images"
    paginate_by = 25

    def get_template_names(self, *args, **kwargs):
        if self.request.htmx:
            return "images/list.html"
        else:
            return self.template_name

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search_query')
        if search_query:
            search_terms = search_query.split()
            queries = [Q(note__icontains=term) for term in search_terms]
            combined_query = queries.pop()

            for query in queries:
                combined_query |= query

            queryset = queryset.filter(combined_query)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = ImageSearchForm(self.request.GET)
        context['language'] = self.request.LANGUAGE_CODE
        context['redirect_to'] = self.request.path
        # Add selected images to the context
        context['selected_images_ids'] = self.request.session.get('selected_images', [])
        return context


class ImageView(generic.DetailView):
    template_name = "images/image.html"
    model = Image

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
            return HttpResponse("", status=200)

        return HttpResponse(status=400)

class ToggleSelectionView(SelectionMixin, View):
    def post(self, request, *args, **kwargs):
        return JsonResponse(self.update_session_selection(request))
