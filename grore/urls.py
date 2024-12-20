"""
URL configuration for grore project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path,re_path
from django.conf.urls.i18n import i18n_patterns
from django.contrib.staticfiles.views import serve
from django.conf import settings
from django.conf.urls.static import static
import os


urlpatterns = [
    path('admin/', admin.site.urls),
    path("__debug__/", include("debug_toolbar.urls")),
    path('i18n/', include('django.conf.urls.i18n')),
]


images_patterns = [
    path("", include("images.urls")),
]

pages_patterns = [
    path("", include("pages.urls")),
]

urlpatterns += i18n_patterns(
    path("", include(images_patterns)),
    path("", include(pages_patterns)),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# if os.environ.get("ENVIRONNEMENT", 'dev').lower() == 'dev':
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
#     print("here")

# print("ENVIRONNEMENT : %s %s" % (settings.STATIC_URL, settings.STATIC_ROOT))