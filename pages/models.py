from django.db import models
from django.urls import reverse

class Page(models.Model):
    slug = models.CharField(max_length=20)
    title = models.CharField(max_length=255)
    content = models.TextField()
    pub_date = models.DateTimeField("date published")

    def get_absolute_url(self):
        return reverse('pages', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title