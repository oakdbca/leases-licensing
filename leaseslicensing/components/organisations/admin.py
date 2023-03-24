from django.contrib import admin
from ledger_api_client.ledger_models import EmailUserRO as EmailUser

from leaseslicensing.components.organisations import models

# Register your models here.


@admin.register(models.Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    list_display = [
        "organisation",
        "organisation_name",
        "organisation_abn",
        "admin_pin_one",
        "admin_pin_two",
        "user_pin_one",
        "user_pin_two",
    ]
    search_fields = (
        "organisation_name",
        "organisation_abn",
        "admin_pin_one",
        "admin_pin_two",
        "user_pin_one",
        "user_pin_two",
    )
    fields = [
        "organisation",
        "organisation_name",
        "organisation_abn",
        "delegates",
        "admin_pin_one",
        "admin_pin_two",
        "user_pin_one",
        "user_pin_two",
        "bpay_allowed",
        "monthly_invoicing_allowed",
        "monthly_invoicing_period",
        "monthly_payment_due_period",
        "apply_application_discount",
        "apply_licence_discount",
        "licence_discount",
        "event_training_completed",
        "event_training_date",
        "charge_once_per_year",
        "last_event_application_fee_date",
        "max_num_months_ahead",
    ]
    readonly_fields = ["organisation_name", "organisation_abn"]

    def organisation_name(self, obj):
        if obj.organisation:
            return obj.organisation["organisation_name"]
        return "No Organisation Assigned"

    organisation_name.short_description = "Ledger Organisation Name"

    def organisation_abn(self, obj):
        if obj.organisation:
            return obj.organisation["organisation_abn"]
        return "No Organisation Assigned"

    organisation_abn.short_description = "Ledger Organisation ABN"


@admin.register(models.OrganisationRequest)
class OrganisationRequestAdmin(admin.ModelAdmin):
    list_display = ["name", "requester", "abn", "status"]


@admin.register(models.OrganisationAccessGroup)
class OrganisationAccessGroupAdmin(admin.ModelAdmin):
    # filter_horizontal = ('members',)
    exclude = ("site",)
    actions = None

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "members":
            # kwargs["queryset"] = EmailUser.objects.filter(email__icontains='@dbca.wa.gov.au')
            kwargs["queryset"] = EmailUser.objects.filter(is_staff=True)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def has_add_permission(self, request):
        return True if models.OrganisationAccessGroup.objects.count() == 0 else False

    def has_delete_permission(self, request, obj=None):
        return False
