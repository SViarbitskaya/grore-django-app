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
from django.contrib.flatpages import views as flatpages_views
from django.conf.urls.i18n import i18n_patterns
from django.contrib.staticfiles.views import serve
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('admin/', admin.site.urls),
    # path('/', include('django.contrib.flatpages.urls')),
    path("__debug__/", include("debug_toolbar.urls")),
    # path("", include("images.urls")),
    path('i18n/', include('django.conf.urls.i18n')),
]

flatpages_patterns = [
    path('pages/', include('django.contrib.flatpages.urls')),
]

images_patterns = [
    path("", include("images.urls")),
]

urlpatterns += i18n_patterns(
    path("", include(images_patterns)),
    path("", include(flatpages_patterns)),
)

# urlpatterns += [
#     re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
# ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)