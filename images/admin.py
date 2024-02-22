from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import Image
from django.db import models
from django.forms import Textarea

class ImageAdmin(TranslationAdmin):
    list_display = ["identifier", "note", "pub_date"]
    search_fields = ["identifier", "note"]
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':4, 'cols':40})},
    }

admin.site.register(Image, ImageAdmin)
