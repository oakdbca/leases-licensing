from django.db import models


class Identifier(models.Model):
    """A class to represent the identifier for a land parcel Eg: R 30490, R 34607 etc."""

    name = models.CharField(max_length=200, unique=True)

    class Meta:
        app_label = "leaseslicensing"
        ordering = ["id"]

    def __str__(self):
        return self.name


class Vesting(models.Model):
    """A class to represent the vesting for a land parcel
    Eg: Conservation Commission Of WA, Marine Parks And Reserves Authority etc."""

    name = models.CharField(max_length=200, unique=True)

    class Meta:
        app_label = "leaseslicensing"
        ordering = ["id"]

    def __str__(self):
        return self.name


class Name(models.Model):
    """A class to represent the name for a land parcel
    Eg: Stirling Range National Park, Dwellingup State Forest etc."""

    name = models.CharField(max_length=200, unique=True)

    class Meta:
        app_label = "leaseslicensing"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Act(models.Model):
    """The legal Act for the land Eg: CALM Act 1984 - Section 5(1)(d), CALM Act 1984 - Section 5(1)(ca)
    etc..."""

    name = models.CharField(max_length=200, unique=True)

    class Meta:
        app_label = "leaseslicensing"
        ordering = ["id"]

    def __str__(self):
        return self.name


class Tenure(models.Model):
    """The tenure for the land Eg: Crown Land, Unallocated Crown Land, Freehold, etc..."""

    name = models.CharField(max_length=200, unique=True)

    class Meta:
        app_label = "leaseslicensing"
        ordering = ["id"]

    def __str__(self):
        return self.name


class Category(models.Model):
    """The category of the land Eg: Nature Reserve, National Park, Conservation Park, etc..."""

    name = models.CharField(max_length=200)

    class Meta:
        app_label = "leaseslicensing"
        ordering = ["id"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


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


class Group(models.Model):
    name = models.CharField(max_length=200, unique=True)

    class Meta:
        app_label = "leaseslicensing"
        ordering = ["name"]

    def __str__(self):
        return self.name


class SiteName(models.Model):
    """A field assessors can use to identify a site (and or group together applications).
    Keeping in it's own model to avoid data duplication"""

    name = models.CharField(max_length=200, unique=True)

    class Meta:
        app_label = "leaseslicensing"
        ordering = ["name"]

    def __str__(self):
        return self.name
