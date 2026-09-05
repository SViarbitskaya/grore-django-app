from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views 
from .views import download_images, download_zip
from django.views.i18n import JavaScriptCatalog

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("jsi18n/", JavaScriptCatalog.as_view(), name="javascript-catalog"),
    path("selection/", views.SelectionView.as_view(), name="selection"),  # Gallery view
    path("selection/delete/<int:image_id>/", views.SelectionView.as_view(), name="delete_image_from_selection"),  # Same view for delete
    path("selection/delete-all/", views.ClearSelectionView.as_view(), name="delete_all_from_selection"),
    path("download-images/", download_images, name='download_images'),
    path("toggle-selection", views.ToggleSelectionView.as_view(), name="toggle_selection"),
    path("download-zip/<int:image_id>/", download_zip, name='download_zip')
]