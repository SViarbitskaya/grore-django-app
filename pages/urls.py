from django.urls import path
from .views import ContactPageView, PageView

from . import views

urlpatterns = [
    path('contact', ContactPageView.as_view(), name='contact'),
    path("pages/<slug:slug>", views.PageView.as_view(), name="page"),

]