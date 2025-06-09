from django.db import models

class Qualification(models.Model):
    qualification_id = models.IntegerField()
    name = models.CharField(max_length=200)
    description = models.TextField()
