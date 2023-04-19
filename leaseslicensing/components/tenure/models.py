from django.db import models


class Region(models.Model):
    name = models.CharField(max_length=200, unique=True)

    class Meta:
        app_label = "leaseslicensing"
        ordering = ["name"]

    def __str__(self):
        return self.name


class District(models.Model):
    region = models.ForeignKey(
        Region, related_name="districts", on_delete=models.PROTECT
    )
    name = models.CharField(max_length=200, unique=True)

    class Meta:
        app_label = "leaseslicensing"
        ordering = ["name"]

    def __str__(self):
        return self.name


class LGA(models.Model):
    """A class to represent a local goverment area (LGA)"""

    name = models.CharField(unique=True, max_length=50, null=False, blank=False)

    class Meta:
        app_label = "leaseslicensing"
        ordering = ["name"]
        verbose_name = "LGA"
        verbose_name_plural = "LGAs"

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)

    class Meta:
        app_label = "leaseslicensing"
        ordering = ["name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name
