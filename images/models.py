from django.db import models
import os


class Image(models.Model):
    identifier = models.CharField(max_length=10)
    note = models.TextField()
    pub_date = models.DateTimeField("date published")
    modif_date = models.DateTimeField("date modified")
    file = models.ImageField()

    def filename(self):
        return os.path.basename(self.file.name)