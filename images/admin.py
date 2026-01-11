from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import Image
from django.db import models
from django.forms import Textarea
from django.utils.html import format_html

class ImageAdmin(TranslationAdmin):
    list_display = ["identifier", "note", "pub_date", "high_res"]
    list_editable = ("high_res",)
    prepopulated_fields = {"slug": ("identifier",)} 
    search_fields = ["identifier", "note"]
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 4, 'cols': 40})},
    }
    fields = ["identifier", "slug", "high_res", "note", "pub_date", "modif_date", "file", "img_preview", "thumbnail", "zoom"]
    readonly_fields = ("img_preview",)
    extra = 0

    def img_preview(self, obj):
        if obj.file:
            return format_html('<img src="{}" width="300"/>', obj.file.url)
        return "No image"
    
    img_preview.short_description = "Image Preview"

admin.site.register(Image, ImageAdmin)