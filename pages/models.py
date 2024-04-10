from django.db import models
import os

class Page(models.Model):
    slug = models.CharField(max_length=20)
    title = models.CharField(max_length=255)
    content = models.TextField(max_length=255)
    pub_date = models.DateTimeField("date published")