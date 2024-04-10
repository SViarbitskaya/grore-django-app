from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.db.models import Q
from django.utils import translation

from .models import Image
from .forms import ImageSearchForm

class HomeView(generic.ListView):
    model = Image
    template_name = "images/index.html"
    context_object_name = "images"
    paginate_by = 5

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

        return context


class ImageView(generic.DetailView):
    template_name = "images/image.html"
    model = Image
