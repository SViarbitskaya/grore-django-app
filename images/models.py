from django.db import models
from django.urls import reverse
from django.utils.html import mark_safe
import os

class Image(models.Model):
    identifier = models.CharField(max_length=255)
    slug = models.SlugField(null=True, unique=True)
    note = models.TextField(max_length=255)
    pub_date = models.DateTimeField("date published")
    modif_date = models.DateTimeField("date modified")
    file = models.ImageField(upload_to="images/")
    thumbnail = models.ImageField(upload_to="thumbs/", blank=True, null=True)
    zoom = models.ImageField(upload_to="zoom/", blank=True, null=True)
    high_res = models.BooleanField(default=False)

    def filename(self):
        return os.path.basename(self.file.name)

    def thumbnail_preview(self):
        if self.thumbnail:
            return mark_safe(u'<img src="%s" />' % self.thumbnail.url)
        return ""
    
    thumbnail_preview.short_description = 'Thumbnail'

    def get_absolute_url(self):
        return reverse("image", kwargs={"slug": self.slug})