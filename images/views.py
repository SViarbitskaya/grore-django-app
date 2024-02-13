from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone

from .models import Image


class HomeView(generic.ListView):
    template_name = "images/index.html"
    context_object_name = "images"
    model = Image
    paginate_by = 16

    # def get_queryset(self):
    #     """
    #     Return the last five published questions (not including those set to be
    #     published in the future).
    #     """
    #     return Image.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[:5]


class ImageView(generic.DetailView):
    template_name = "images/image.html"
    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Image.objects.filter(pub_date__lte=timezone.now())
