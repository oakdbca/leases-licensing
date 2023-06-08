from django.contrib import admin
from leaseslicensing.components.texts.models import (
    DetailsText,
)

@admin.register(DetailsText)
class DetailsTextsAdmin(admin.ModelAdmin):
    list_display = ["target", "body"]
