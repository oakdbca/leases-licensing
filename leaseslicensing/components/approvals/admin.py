from django import forms as forms
from django.contrib import admin
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


class ApprovalTypeDocumentTypeOnApprovalTypeForm(forms.ModelForm):
    class Meta:
        model = models.ApprovalType
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        approval_type = cleaned_data.get("approval_type")
        document_type = cleaned_data.get("approval_type_document_type")
        is_mandatory = cleaned_data.get("mandatory", False)

        # Why would a specifically typed document type be anything but mandatory? We enforce this here.
        if document_type.is_typed and not is_mandatory:
            raise ValidationError(
                f"{document_type.type_display} {document_type} is a typed document type and must be mandatory."
            )

        query_dict = {
            "is_license_document": document_type.is_license_document,
            "is_cover_letter": document_type.is_cover_letter,
            "is_sign_off_sheet": document_type.is_sign_off_sheet,
        }
        # Existing approval documents of this typed document type
        existing_documents = (
            approval_type.approvaltypedocumenttypes.all()
            .filter(**query_dict)
            .exclude(pk=document_type.pk)
        )
        if existing_documents.exists():
            raise ValidationError(
                f"There is already a document of the same type for this approval type: {existing_documents.first()}"
            )


class ApprovalTypeDocumentTypeOnApprovalTypeInline(admin.TabularInline):
    model = models.ApprovalTypeDocumentTypeOnApprovalType
    extra = 0
    verbose_name = "Document Type"
    verbose_name_plural = "Document Types"

    form = ApprovalTypeDocumentTypeOnApprovalTypeForm


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


@admin.register(models.ApprovalTransfer)
class ApprovalTransferAdmin(admin.ModelAdmin):
    list_display = (
        "lodgement_number",
        "approval",
        "transferee_type",
        "transferee",
        "processing_status",
        "datetime_created",
        "datetime_updated",
        "datetime_expiry",
    )
