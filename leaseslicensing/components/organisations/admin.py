from django.contrib import admin

from leaseslicensing.components.organisations import models


class UserDelegationInline(admin.TabularInline):
    model = models.UserDelegation
    extra = 0


@admin.register(models.Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    list_display = [
        "ledger_organisation_id",
        "ledger_organisation_name",
        "ledger_organisation_abn",
        "admin_pin_one",
        "admin_pin_two",
        "user_pin_one",
        "user_pin_two",
    ]
    search_fields = (
        "ledger_organisation_name",
        "ledger_organisation_abn",
        "admin_pin_one",
        "admin_pin_two",
        "user_pin_one",
        "user_pin_two",
    )
    fields = [
        "ledger_organisation_id",
        "ledger_organisation_name",
        "ledger_organisation_trading_name",
        "ledger_organisation_abn",
        "ledger_organisation_email",
        "admin_pin_one",
        "admin_pin_two",
        "user_pin_one",
        "user_pin_two",
    ]
    readonly_fields = [
        "ledger_organisation_name",
        "ledger_organisation_trading_name",
        "ledger_organisation_abn",
        "ledger_organisation_email",
        "admin_pin_one",
        "admin_pin_two",
        "user_pin_one",
        "user_pin_two",
    ]

    def ledger_organisation_name(self, obj):
        if obj.organisation:
            return obj.organisation["ledger_organisation_name"]
        return "No Organisation Assigned"

    ledger_organisation_name.short_description = "Ledger Organisation Name"

    def ledger_organisation_trading_name(self, obj):
        if obj.organisation:
            return obj.organisation["ledger_organisation_trading_name"]
        return "No Organisation Assigned"

    def ledger_organisation_abn(self, obj):
        if obj.organisation:
            return obj.organisation["ledger_organisation_abn"]
        return "No Organisation Assigned"

    ledger_organisation_abn.short_description = "Ledger Organisation ABN"

    def ledger_organisation_email(self, obj):
        if obj.organisation:
            return obj.organisation["ledger_organisation_email"]
        return "No Organisation Assigned"

    ledger_organisation_email.short_description = "Ledger Organisation ABN"


@admin.register(models.OrganisationRequest)
class OrganisationRequestAdmin(admin.ModelAdmin):
    list_display = ["ledger_organisation_name", "requester", "abn", "status"]

    def ledger_organisation_name(self, obj):
        if obj.organisation:
            return obj.organisation.ledger_organisation_name
        if obj.name:
            return obj.name


@admin.register(models.OrganisationContact)
class OrganisationContact(admin.ModelAdmin):
    list_display = ["ledger_organisation_name", "full_name", "user_status", "user_role"]
    ordering = ["organisation", "-user_status", "first_name"]

    def ledger_organisation_name(self, obj):
        if obj.organisation:
            return obj.organisation.ledger_organisation_name
