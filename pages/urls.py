from django.urls import path
from .views import ContactPageView, AboutPageView

from . import views

urlpatterns = [
    path('pages/about/', AboutPageView.as_view(), name='about'),
    path('pages/contact/', ContactPageView.as_view(), name='contact'),
]