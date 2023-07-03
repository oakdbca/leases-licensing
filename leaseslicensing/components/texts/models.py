from django.db import models

from ckeditor.fields import RichTextField

class DetailsText(models.Model):
    body = RichTextField(blank=False, null=False)
    target = models.CharField("Target", max_length=128) # HTML target

    class Meta:
        app_label = "leaseslicensing"
        verbose_name = "Details Text"
        verbose_name_plural = "Details Texts"

    def __str__(self):
        return self.target.replace("-", " ").replace("_", " ")
