from django.db import models

# Create your models here.


class Catalogue(models.Model):
    name = models.CharField(max_length=25)
    description = models.TextField(max_length=100)
