from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views 
from .views import download_images

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("selection/", views.SelectionView.as_view(), name="selection"),  # Gallery view
    path("selection/delete/<int:image_id>/", views.SelectionView.as_view(), name="delete_image_from_selection"),  # Same view for delete
    path('download-images/', download_images, name='download_images'),
    path("toggle-selection", views.ToggleSelectionView.as_view(), name="toggle_selection"),
]