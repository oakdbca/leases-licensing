from django.contrib import admin

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
    list_display = (
        "name",
        "details_placeholder",
        "gst_free",
    )
    inlines = [
        ApprovalTypeDocumentTypeOnApprovalTypeInline,
    ]
