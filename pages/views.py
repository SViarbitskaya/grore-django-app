from django.shortcuts import render
from django.views.generic import TemplateView, DetailView
from .models import Page

class ContactPageView(TemplateView):
    template_name = 'contact.html'

class PageView(DetailView):
    template_name = 'page.html'
    model = Page

