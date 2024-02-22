from django.shortcuts import render
from django.views.generic import TemplateView

class ContactPageView(TemplateView):
    template_name = 'contact.html'

class AboutPageView(TemplateView):
    template_name = 'about.html'

