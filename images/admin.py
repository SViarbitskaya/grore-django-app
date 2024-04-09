from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import Image
from django.db import models
from django.forms import Textarea
from django.utils.html import format_html

class ImageAdmin(TranslationAdmin):
    list_display = ["identifier", "note", "pub_date"]
    search_fields = ["identifier", "note"]
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':4, 'cols':40})},
    }

    fields = ["identifier", "note", "pub_date", "modif_date", "file", "img_preview", ]

    # add img_preview
    readonly_fields = ("img_preview",)
    extra = 0

    def img_preview(self, obj):
        return format_html('<img src="{}" width="300"/>', obj.file.url)

    img_preview.short_description = "Image Preview"

admin.site.register(Image, ImageAdmin)
