from django.contrib import admin

from leaseslicensing.components.invoicing import models


@admin.register(models.ChargeMethod)
class ChargeMethodAdmin(admin.ModelAdmin):
    list_display = [
        "key",
        "display_name",
        "display_order",
    ]
    # max_num = 0  # This removes 'Add another ...' button
    readonly_fields = ("key",)

    def has_add_permission(self, request, obj=None):
        # Remove 'Add ...' button
        return False

    def has_delete_permission(self, request, obj=None):
        # Remove 'Delete'
        return False


@admin.register(models.ConsumerPriceIndex)
class ConsumerPriceIndexAdmin(admin.ModelAdmin):
    list_display = [
        "year",
        "quarter",
        "value",
        "datetime_created",
    ]
    list_display_links = [
        "year",
        "quarter",
        "value",
        "datetime_created",
    ]
    readonly_fields = ("year", "quarter", "value", "datetime_created")

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(models.RepetitionType)
class RepetitionTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(models.CPICalculationMethod)
class CPICalculationMethodAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "display_name",
        "quarter",
        "archived",
    ]
    list_display_links = [
        "name",
        "display_name",
        "archived",
    ]
    fields = (
        "name",
        "quarter",
        "display_name",
        "archived",
    )
    readonly_fields = ("name", "display_name")

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return False


class InvoiceTransactionInline(admin.TabularInline):
    model = models.InvoiceTransaction
    extra = 0


@admin.register(models.Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    inlines = [
        InvoiceTransactionInline,
    ]
