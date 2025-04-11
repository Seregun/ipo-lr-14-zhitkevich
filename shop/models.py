from django.db import models

class Qualification(models.Model):
    qualification_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.qualification_id} - {self.name}"