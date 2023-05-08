from django.contrib import admin
from django import forms as django_forms
from leaseslicensing.components.approvals import models



@admin.register(models.ApprovalTypeDocumentType)
class ApprovalTypeDocumentTypeAdmin(admin.ModelAdmin):
    pass


class ApprovalTypeDocumentTypeOnApprovalTypeInline(admin.TabularInline):
    model = models.ApprovalTypeDocumentTypeOnApprovalType
    extra = 0
    verbose_name = "Document Type"
    verbose_name_plural = "Document Types"


@admin.register(models.ApprovalType)
class ApprovalTypeAdmin(admin.ModelAdmin):
    inlines = [
        ApprovalTypeDocumentTypeOnApprovalTypeInline,
        ]

