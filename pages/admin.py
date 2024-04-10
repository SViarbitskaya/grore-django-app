from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import Page
from django.db import models
from django.forms import Textarea

class PageAdmin(TranslationAdmin):
    list_display = ["title", "pub_date"]
    search_fields = ["title"]
    # formfield_overrides = {
    #     models.TextField: {'widget': Textarea(attrs={'rows':4, 'cols':40})},
    # }

admin.site.register(Page, PageAdmin)
