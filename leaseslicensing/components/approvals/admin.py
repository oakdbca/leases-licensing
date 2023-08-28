from django.contrib import admin
from django import forms as forms
from django.core.exceptions import ValidationError
from leaseslicensing.components.approvals import models


class ApprovalTypeDocumentTypeForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        is_license_document = cleaned_data.get("is_license_document")
        is_cover_letter = cleaned_data.get("is_cover_letter")
        is_sign_off_sheet = cleaned_data.get("is_sign_off_sheet")

        if is_license_document + is_cover_letter + is_sign_off_sheet > 1:
            raise ValidationError("An Approval document can only be of one or no type.")


def document_type(obj):
    # This function is used to display the document type in the admin list view
    if obj.is_license_document:
        return "License Document"
    elif obj.is_cover_letter:
        return "Cover Letter"
    elif obj.is_sign_off_sheet:
        return "Sign Off Sheet"
    else:
        return "Other"


document_type.short_description = "Document Type"


@admin.register(models.ApprovalTypeDocumentType)
class ApprovalTypeDocumentTypeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        document_type,
    )
    fieldsets = [
        ("Document Name", {"fields": ["name"]}),
        (
            "Document Type",
            {
                "fields": [
                    ("is_license_document", "is_cover_letter", "is_sign_off_sheet")
                ]
            },
        ),
    ]

    form = ApprovalTypeDocumentTypeForm

    def get_form(self, request, obj=None, change=False, **kwargs):
        # Overwrite the default form to change the labels of the checkboxes
        form = super().get_form(request, obj, change, **kwargs)
        form.base_fields["is_license_document"].label = "License Document"
        form.base_fields["is_cover_letter"].label = "Cover Letter"
        form.base_fields["is_sign_off_sheet"].label = "Sign Off Sheet"
        return form


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
