from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import Page
from django.db import models
from django_ckeditor_5.widgets import CKEditor5Widget

class PageAdmin(TranslationAdmin):
    list_display = ["title", "pub_date"]
    search_fields = ["title"]
    formfield_overrides = {
        models.TextField: {'widget': CKEditor5Widget(config_name='default')},
    }

admin.site.register(Page, PageAdmin)
