"""
Django settings for grore project.

Generated by 'django-admin startproject' using Django 5.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
from django.utils.translation import gettext_lazy as _
import os
import mimetypes            

from dotenv import load_dotenv # Pour les variables d'.env

# Prendre les variables d'environnement
load_dotenv()

# Check to see if basic variables needed are defined

REQUIRED = ["DB_DATABASE"]

needs_required = []
for i in REQUIRED:
  if not os.getenv(i) != '':
    needs_required.append(i)


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
#SECRET_KEY = 'django-insecure-5(o@$_j%hfn*smdqdut9o$ya18r^kg!-7#lc6dh(g*ijn!2j_0'
SECRET_KEY = os.environ.get("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
if os.environ.get("DEBUG", 'false').lower == 'true':
    DEBUG = true

# 'DJANGO_ALLOWED_HOSTS' should be a single string of hosts with a space between each.
# For example: 'DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1]'
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS","localhost 127.0.0.1").replace(",","").split(" ")

# Application definition

INSTALLED_APPS = [
    "pages.apps.PagesConfig",
    "images.apps.ImagesConfig",
    'modeltranslation',
    "django_htmx",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'debug_toolbar',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    "django_htmx.middleware.HtmxMiddleware",
]

CSRF_TRUSTED_ORIGINS = [  os.getenv('WEB_PROTO','http') + '://' +  os.getenv('DJANGO_HOST','localhost') + ':' +  os.getenv('DJANGO_PORT','8000'),
                           os.getenv('WEB_PROTO','http') + '://' +  os.getenv('WEB_DOMAIN','localhost') 
                        ];

# CSRF_TRUSTED_ORIGINS = [
#     'http://localhost:1337',  # The port you're running on
#     'http://127.0.0.1:1337',
# ]

ROOT_URLCONF = 'grore.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        "DIRS": [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'grore.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": os.environ.get("DB_ENGINE", "django.db.backends."),
        "NAME": os.environ.get("DB_DATABASE", BASE_DIR / "db.sqlite3"),
        "USER": os.environ.get("DB_USER", "user"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "password"),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]



# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

USE_I18N = True

LANGUAGE_CODE = os.environ.get("DJANGO_LANGUAGE_CODE", 'en-us')

LANGUAGES = [
    ("en", _("English")),
    ("fr", _("French")),
]

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),  # Create a 'locale' directory in your project's base directory
]

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = os.environ.get("DJANGO_STATIC_URL", '/static') + '/'
STATIC_ROOT = os.environ.get("DJANGO_STATIC_ROOT", BASE_DIR / "staticfiles")

MEDIA_URL = os.environ.get("DJANGO_MEDIA_URL", '/media') + '/'
MEDIA_ROOT = os.environ.get("DJANGO_MEDIA_ROOT", BASE_DIR / "media")

# STATICFILES_DIRS = [
#     BASE_DIR / "static",
#     "/static/",
# ]

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

INTERNAL_IPS = [
    "127.0.0.1",
    "localhost",
    '0.0.0.0'
]


# MEDIA_ROOT =  os.path.join(BASE_DIR, 'media')
# MEDIA_URL = '/media/'

# from .settings_prod import *
