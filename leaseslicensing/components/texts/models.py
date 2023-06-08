from django.db import models

class DetailsText(models.Model):
    body = models.CharField("Text body", max_length=1024) # Text body
    target = models.CharField("Target", max_length=128) # HTML target

    class Meta:
        app_label = "leaseslicensing"
        verbose_name = "Details Text"
        verbose_name_plural = "Details Texts"

    def __str__(self):
        return self.body
