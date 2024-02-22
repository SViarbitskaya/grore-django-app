from django.urls import path
from .views import ContactPageView, AboutPageView

from . import views

urlpatterns = [
    path('about/', AboutPageView.as_view(), name='about'),
    path('contact/', ContactPageView.as_view(), name='contact'),
]