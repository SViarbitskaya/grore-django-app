from django.contrib import admin

from .models import Image

class ImageAdmin(admin.ModelAdmin):
    list_display = ["identifier", "note", "pub_date"]
    search_fields = ["identifier", "note"]

admin.site.register(Image, ImageAdmin)
