from django.db import models


class Image(models.Model):
    identifier = models.CharField(max_length=10)
    note = models.CharField(max_length=255)
    pub_date = models.DateTimeField("date published")
    modif_date = models.DateTimeField("date modified")
    file = models.ImageField(upload_to="images")