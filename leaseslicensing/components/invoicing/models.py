import logging
import math
import uuid
from datetime import datetime
from decimal import Decimal

import pytz
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg, F, Sum, Window
from django.db.models.functions import Coalesce
from django.forms import ValidationError
from django.utils import timezone
from ledger_api_client import settings_base

from leaseslicensing.components.invoicing.exceptions import NoChargeMethod
from leaseslicensing.components.main.models import (
    LicensingModel,
    RevisionedMixin,
    SecureFileField,
)

PERCENTAGE_VALIDATOR = [MinValueValidator(0.0), MaxValueValidator(100)]

logger = logging.getLogger(__name__)


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    modified_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True


class ChargeMethod(models.Model):
    key = models.CharField(max_length=200, unique=True)
    display_name = models.CharField(
        max_length=200,
    )
    display_order = models.IntegerField(default=0)

    class Meta:
        app_label = "leaseslicensing"
        ordering = ["display_order"]

    def __str__(self):
        return self.display_name


class RepetitionType(models.Model):
    key = models.CharField(max_length=200, unique=True)
    display_name = models.CharField(
        max_length=200,
    )

    class Meta:
        app_label = "leaseslicensing"
        ordering = ["id"]

    def __str__(self):
        return self.display_name


class ReviewDateAnnually(BaseModel):
    review_date = models.DateField(null=True, blank=True)
    date_of_enforcement = models.DateField()

    class Meta:
        app_label = "leaseslicensing"
        verbose_name_plural = "Review Date Annually"

    @staticmethod
    def get_review_date_annually_by_date(
        target_date=datetime.now(pytz.timezone(settings_base.TIME_ZONE)).date(),
    ):
        """
        Return an setting object which is enabled at the target_date
        """
        review_date_annually = (
            ReviewDateAnnually.objects.filter(
                date_of_enforcement__lte=target_date,
            )
            .order_by("date_of_enforcement")
            .last()
        )
        return review_date_annually


class ReviewDateQuarterly(BaseModel):
    review_date_q1 = models.DateField()
    review_date_q2 = models.DateField()
    review_date_q3 = models.DateField()
    review_date_q4 = models.DateField()
    date_of_enforcement = models.DateField()

    class Meta:
        app_label = "leaseslicensing"
        verbose_name_plural = "Review Date Quarterly"

    @staticmethod
    def get_review_date_quarterly_by_date(
        target_date=datetime.now(pytz.timezone(settings_base.TIME_ZONE)).date(),
    ):
        """
        Return an setting object which is enabled at the target_date
        """
        review_date_quarterly = (
            ReviewDateQuarterly.objects.filter(
                date_of_enforcement__lte=target_date,
            )
            .order_by("date_of_enforcement")
            .last()
        )
        return review_date_quarterly


class ReviewDateMonthly(BaseModel):
    review_date = models.PositiveSmallIntegerField(null=True, blank=True)
    date_of_enforcement = models.DateField()

    class Meta:
        app_label = "leaseslicensing"
        verbose_name_plural = "Review Date Monthly"

    @staticmethod
    def get_review_date_monthly_by_date(
        target_date=datetime.now(pytz.timezone(settings_base.TIME_ZONE)).date(),
    ):
        """
        Return an setting object which is enabled at the target_date
        """
        review_date_monthly = (
            ReviewDateMonthly.objects.filter(
                date_of_enforcement__lte=target_date,
            )
            .order_by("date_of_enforcement")
            .last()
        )
        return review_date_monthly


class InvoicingAndReviewDatesManager(models.Manager):
    def get_queryset(self):
        # Only show the current and future year
        return (
            super()
            .get_queryset()
            .filter(year__gte=timezone.now().year, year__lte=timezone.now().year + 10)
        )


class InvoicingAndReviewDates(BaseModel):
    objects = InvoicingAndReviewDatesManager()

    year = models.PositiveSmallIntegerField(editable=False)

    invoicing_date_annually = models.DateField(help_text="Invoice every year on")
    invoicing_day_for_quarter = models.PositiveSmallIntegerField(
        default=1,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(30),  # MAR, JUN, SEP, DEC all have at least 30 days
        ],
        help_text="Day of the month to generate and send invoices every quarter (MAR, JUN, SEP, DEC)",
    )
    invoicing_day_for_month = models.PositiveSmallIntegerField(
        default=1,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(28),  # Every month of the years has at least 28 days
        ],
    )

    review_date_annually = models.DateField(help_text="Review every year on")
    review_day_for_quarter = models.PositiveSmallIntegerField(
        default=1,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(30),  # MAR, JUN, SEP, DEC all have at least 30 days
        ],
        help_text="Day of the month to send review reminder every quarter (MAR, JUN, SEP, DEC)",
    )
    review_day_for_month = models.PositiveSmallIntegerField(
        default=1,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(28),  # Every month of the years has at least 28 days
        ],
    )

    class Meta:
        app_label = "leaseslicensing"
        verbose_name_plural = "Invoicing and Review Dates"
        ordering = ["year"]

    def __str__(self):
        return f"Invoicing and Review Dates for {self.year}"

    def clean(self):
        if self.invoicing_date_annually.year != self.year:
            raise ValidationError(
                {
                    "invoicing_date_annually": f"The annual invoicing date must be in {self.year}"
                }
            )

        if self.review_date_annually.year != self.year:
            raise ValidationError(
                {
                    "review_date_annually": f"The annual review date must be in {self.year}"
                }
            )


class InvoicingDateAnnually(BaseModel):
    invoicing_date = models.DateField(null=True, blank=True)
    date_of_enforcement = models.DateField()

    class Meta:
        app_label = "leaseslicensing"
        verbose_name_plural = "Invoicing Date Annually"

    @staticmethod
    def get_invoicing_date_annually_by_date(
        target_date=datetime.now(pytz.timezone(settings_base.TIME_ZONE)).date(),
    ):
        """
        Return an setting object which is enabled at the target_date
        """
        invoicing_date_annually = (
            InvoicingDateAnnually.objects.filter(
                date_of_enforcement__lte=target_date,
            )
            .order_by("date_of_enforcement")
            .last()
        )
        return invoicing_date_annually


class InvoicingDateQuarterly(BaseModel):
    invoicing_date_q1 = models.DateField()
    invoicing_date_q2 = models.DateField()
    invoicing_date_q3 = models.DateField()
    invoicing_date_q4 = models.DateField()
    date_of_enforcement = models.DateField()

    class Meta:
        app_label = "leaseslicensing"
        verbose_name_plural = "Invoicing Date Quarterly"

    @staticmethod
    def get_invoicing_date_quarterly_by_date(
        target_date=datetime.now(pytz.timezone(settings_base.TIME_ZONE)).date(),
    ):
        """
        Return an setting object which is enabled at the target_date
        """
        invoicing_date_quarterly = (
            InvoicingDateQuarterly.objects.filter(
                date_of_enforcement__lte=target_date,
            )
            .order_by("date_of_enforcement")
            .last()
        )
        return invoicing_date_quarterly


class InvoicingDateMonthly(BaseModel):
    invoicing_date = models.PositiveSmallIntegerField(null=True, blank=True)
    date_of_enforcement = models.DateField()

    class Meta:
        app_label = "leaseslicensing"
        verbose_name_plural = "Invoicing Date Monthly"

    @staticmethod
    def get_invoicing_date_monthly_by_date(
        target_date=datetime.now(pytz.timezone(settings_base.TIME_ZONE)).date(),
    ):
        """
        Return an setting object which is enabled at the target_date
        """
        invoicing_date_monthly = (
            InvoicingDateMonthly.objects.filter(
                date_of_enforcement__lte=target_date,
            )
            .order_by("date_of_enforcement")
            .last()
        )
        return invoicing_date_monthly


def get_year():
    cpis = ConsumerPriceIndex.objects.all()
    if cpis:
        latest_cpis = cpis.order_by("year").last()
        return getattr(latest_cpis, "year") + 1
    else:
        return ConsumerPriceIndex.start_year


class ConsumerPriceIndex(BaseModel):
    time_period = models.CharField(max_length=7, help_text="Year and Quarter")
    value = models.DecimalField(
        max_digits=20,
        decimal_places=1,
        help_text="Percentage Change from Corresponding Quarter of the Previous Year",
    )
    datetime_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "leaseslicensing"
        verbose_name = "CPI Data (Perth - All Groups)"
        verbose_name_plural = "CPI Data (Perth - All Groups)"

    def __str__(self):
        return f"{self.time_period}: {self.value}"


class CPICalculationMethod(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False, editable=False)
    display_name = models.CharField(max_length=255, null=False, blank=False)
    archived = models.BooleanField(default=False)

    class Meta:
        app_label = "leaseslicensing"
        verbose_name = "CPI Calculation Method"
        verbose_name_plural = "CPI Calculation Methods"

    def __str__(self):
        return f"{self.display_name}"


class InvoicingDetailsManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related(
                "annual_increment_amounts",
                "annual_increment_percentages",
                "gross_turnover_percentages",
                "crown_land_rent_review_dates",
            )
        )


class InvoicingDetails(BaseModel):
    """
    This is the main model to store invoicing details, generated by a proposal first
    (Proposal has a field: invoicing_details)
    then copied and/or edited as business run
    """

    objects = InvoicingDetailsManager()

    charge_method = models.ForeignKey(
        ChargeMethod, null=True, blank=True, on_delete=models.SET_NULL
    )
    base_fee_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    once_off_charge_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    review_once_every = models.PositiveSmallIntegerField(
        null=True, blank=True, default=1
    )
    review_repetition_type = models.ForeignKey(
        RepetitionType,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="invoicing_details_set_for_review",
    )
    invoicing_once_every = models.PositiveSmallIntegerField(
        null=True, blank=True, default=1
    )
    invoicing_repetition_type = models.ForeignKey(
        RepetitionType,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="invoicing_details_set_for_invoicing",
    )
    previous_invoicing_details = models.OneToOneField(
        "self",
        null=True,
        blank=True,
        related_name="next_invoicing_details",
        on_delete=models.SET_NULL,
    )
    cpi_calculation_method = models.ForeignKey(
        CPICalculationMethod,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="invoicing_details",
    )

    class Meta:
        app_label = "leaseslicensing"

    def __str__(self):
        return f"Invoicing Details for Approval: {self.proposal.approval} (Current Proposal: {self.proposal})"

    @property
    def approval(self):
        if not hasattr(self, "proposal") or not self.proposal:
            return None
        if not hasattr(self.proposal, "approval") or not self.proposal.approval:
            return None

        return self.proposal.approval

    def base_fee_plus_cpi(self):
        logger.debug(f"Base Fee: {self.base_fee_amount}")
        if not self.cpi_calculation_method:
            logger.warn(
                f"No CPI calculation method set for Invoicing Details: {self.id}"
            )
            return self.base_fee_amount

        logger.debug(f"CPI Calculation Method: {self.cpi_calculation_method}")

        if (
            settings.CPI_CALCULATION_METHOD_LATEST_MAR_QUARTER
            == self.cpi_calculation_method.display_name
        ):
            cpi_value = (
                ConsumerPriceIndex.objects.filter(time_period__contains="Q1")
                .last()
                .value
            )

        if (
            settings.CPI_CALCULATION_METHOD_LATEST_JUN_QUARTER
            == self.cpi_calculation_method.name
        ):
            cpi_value = (
                ConsumerPriceIndex.objects.filter(time_period__contains="Q2")
                .last()
                .value
            )

        if (
            settings.CPI_CALCULATION_METHOD_LATEST_SEP_QUARTER
            == self.cpi_calculation_method.name
        ):
            cpi_value = (
                ConsumerPriceIndex.objects.filter(time_period__contains="Q3")
                .last()
                .value
            )

        if (
            settings.CPI_CALCULATION_METHOD_LATEST_DEC_QUARTER
            == self.cpi_calculation_method.name
        ):
            cpi_value = (
                ConsumerPriceIndex.objects.filter(time_period__contains="Q4")
                .last()
                .value
            )

        if (
            settings.CPI_CALCULATION_METHOD_LATEST_QUARTER
            == self.cpi_calculation_method.name
        ):
            cpi_value = ConsumerPriceIndex.objects.last().value

        if (
            settings.CPI_CALCULATION_METHOD_AVERAGE_LATEST_FOUR_QUARTERS
            == self.cpi_calculation_method.name
        ):
            cpi_value = (
                ConsumerPriceIndex.objects.all()
                .order_by("-time_period")[:4]
                .aggregate(Avg("value"))["value__avg"]
            )

        logger.debug(f"CPI Percentage: {cpi_value}")

        return Decimal(self.base_fee_amount * (1 + cpi_value / 100)).quantize(
            Decimal("0.01")
        )

    @property
    def total_invoice_count(self):
        start_date = self.approval.start_date
        expiry_date = self.approval.expiry_date
        days_difference = relativedelta(start_date, expiry_date).days
        logger.debug(f"Days Difference: {days_difference}")
        years_difference = days_difference / 365
        whole_years_difference = math.ceil(years_difference)
        logger.debug(f"Whole Years Difference: {whole_years_difference}")
        # Return how many invoices in total will be generated based on this invoicing details
        if settings.REPETITION_TYPE_ANNUALLY == self.invoicing_repetition_type.key:
            return whole_years_difference

        if settings.REPETITION_TYPE_QUARTERLY == self.invoicing_repetition_type.key:
            return whole_years_difference * 4

        if settings.REPETITION_TYPE_MONTHLY == self.invoicing_repetition_type.key:
            return whole_years_difference * 12

    @property
    def invoices_created(self):
        return Invoice.objects.filter(invoicing_details=self)

    @property
    def invoices_yet_to_be_generated(self):
        return self.total_invoice_count - self.invoices_created

    @property
    def invoice_amount(self):
        annual_amount = Decimal("0.00")

        if not self.charge_method:
            raise NoChargeMethod(f"No charge method found on {self}")

        logger.debug(f"\nCharge Method: {self.charge_method}")

        if self.charge_method.key == settings.CHARGE_METHOD_NO_RENT_OR_LICENCE_CHARGE:
            return annual_amount

        if self.charge_method.key == settings.CHARGE_METHOD_ONCE_OFF_CHARGE:
            return self.once_off_charge_amount

        if self.charge_method.key == settings.CHARGE_METHOD_BASE_FEE_PLUS_ANNUAL_CPI:
            annual_amount = self.base_fee_plus_cpi()

        if (
            self.charge_method.key
            == settings.CHARGE_METHOD_BASE_FEE_PLUS_FIXED_ANNUAL_INCREMENT
        ):
            increment_amount_for_this_year = self.annual_increment_amounts.filter(
                year=timezone.now().year
            )
            if not increment_amount_for_this_year:
                logger.warn(
                    f"No annual increment amount found for Invoicing Details: {self.id} for year: {timezone.now().year}"
                )
                return self.base_fee
            annual_amount = self.base_fee + increment_amount_for_this_year

        if (
            self.charge_method.key
            == settings.CHARGE_METHOD_BASE_FEE_PLUS_FIXED_ANNUAL_PERCENTAGE
        ):
            increment_percentage_for_this_year = (
                self.annual_increment_percentages.filter(year=timezone.now().year)
            )
            if not increment_percentage_for_this_year:
                logger.warn(
                    f"No annual increment percentage found for Invoicing Details: {self.id} "
                    f"for year: {timezone.now().year}"
                )
                return self.base_fee
            annual_amount = self.base_fee * (
                1 + increment_percentage_for_this_year / 100
            )

        if (
            self.charge_method.key
            == settings.CHARGE_METHOD_PERCENTAGE_OF_GROSS_TURNOVER
        ):
            gross_turnover_for_previous_financial_year = (
                self.gross_turnover_percentages.get(year=timezone.now().year)
            )
            annual_amount = (
                gross_turnover_for_previous_financial_year.gross_turnover
                * (1 + gross_turnover_for_previous_financial_year.percentage / 100)
            )

        if settings.REPETITION_TYPE_ANNUALLY == self.invoicing_repetition_type.key:
            return Decimal(annual_amount).quantize(Decimal("0.01"))

        if settings.REPETITION_TYPE_QUARTERLY == self.invoicing_repetition_type.key:
            return Decimal(annual_amount / 4).quantize(Decimal("0.01"))

        if settings.REPETITION_TYPE_MONTHLY == self.invoicing_repetition_type.key:
            return Decimal(annual_amount / 12).quantize(Decimal("0.01"))


class FixedAnnualIncrementAmount(BaseModel):
    year = models.PositiveSmallIntegerField(null=True, blank=True)
    increment_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default="0.00", null=True, blank=True
    )
    invoicing_details = models.ForeignKey(
        InvoicingDetails,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="annual_increment_amounts",
    )

    class Meta:
        app_label = "leaseslicensing"
        ordering = [
            "year",
        ]

    @property
    def readonly(self):
        # TODO: implement
        return False


class FixedAnnualIncrementPercentage(BaseModel):
    year = models.PositiveSmallIntegerField(null=True, blank=True)
    increment_percentage = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default="0.0",
        blank=True,
        null=True,
        validators=PERCENTAGE_VALIDATOR,
    )
    invoicing_details = models.ForeignKey(
        InvoicingDetails,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="annual_increment_percentages",
    )

    class Meta:
        app_label = "leaseslicensing"
        ordering = [
            "year",
        ]

    @property
    def readonly(self):
        # TODO: implement
        return False


class PercentageOfGrossTurnover(BaseModel):
    year = models.PositiveSmallIntegerField(null=True, blank=True)
    percentage = models.DecimalField(
        max_digits=4, decimal_places=1, default="0.0", null=True, blank=True
    )
    gross_turnover = models.DecimalField(
        null=True, blank=True, max_digits=10, decimal_places=2
    )
    invoicing_details = models.ForeignKey(
        InvoicingDetails,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="gross_turnover_percentages",
    )

    class Meta:
        app_label = "leaseslicensing"
        ordering = [
            "year",
        ]

    def __str__(self):
        return f"{self.year}: {self.percentage}%"

    @property
    def readonly(self):
        # TODO: implement
        return False

    @property
    def financial_year(self):
        return f"{self.year-1}-{self.year}"


class CrownLandRentReviewDate(BaseModel):
    review_date = models.DateField(null=True, blank=True)
    invoicing_details = models.ForeignKey(
        InvoicingDetails,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="crown_land_rent_review_dates",
    )

    class Meta:
        app_label = "leaseslicensing"
        ordering = [
            "review_date",
        ]

    @property
    def readonly(self):
        # TODO: implement
        return False


class LeaseLicenceFee(BaseModel):
    """
    This model handles each invoice and the information surrounding it.
    An object of this model is created at an invoicing date.
    """

    invoicing_details = models.ForeignKey(
        InvoicingDetails,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="lease_licence_fees",
    )
    invoice_reference = models.CharField(
        max_length=50, null=True, blank=True, default=""
    )
    invoice_cover_start_date = models.DateField(null=True, blank=True)
    invoice_cover_end_date = models.DateField(null=True, blank=True)
    date_invoice_sent = models.DateField(null=True, blank=True)

    class Meta:
        app_label = "leaseslicensing"

    def __str__(self):
        if self.invoicing_details.approval:
            return f"Approval: {self.invoicing_details.approval}, Invoice: {self.invoice_reference}"
        else:
            return (
                f"Proposal: {self.invoicing_details}, Invoice: {self.invoice_reference}"
            )

    @property
    def invoice(self):
        invoice = None
        if self.invoice_reference:
            invoice = Invoice.objects.get(reference=self.invoice_reference)
        return invoice

    @property
    def amount(self):
        amount = None
        if self.invoice_reference:
            invoice = Invoice.objects.get(reference=self.invoice_reference)
            amount = invoice.amount
        return amount


def invoice_pdf_upload_path(instance, filename):
    return f"approvals/{instance.approval.id}/invoices/{instance.id}/{filename}"


class InvoiceManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("approval")
            .prefetch_related("transactions")
        )


class Invoice(LicensingModel):
    objects = InvoiceManager()

    MODEL_PREFIX = "I"

    INVOICE_STATUS_UNPAID = "unpaid"
    INVOICE_STATUS_PAID = "paid"
    INVOICE_STATUS_VOID = "void"
    INVOICE_STATUS_CHOICES = (
        (INVOICE_STATUS_UNPAID, "Unpaid"),
        (INVOICE_STATUS_PAID, "Paid"),
        (INVOICE_STATUS_VOID, "Void"),
    )
    approval = models.ForeignKey(
        "Approval",
        blank=False,
        null=False,
        on_delete=models.PROTECT,
        related_name="invoices",
    )
    status = models.CharField(
        max_length=40,
        choices=INVOICE_STATUS_CHOICES,
        default=INVOICE_STATUS_UNPAID,
        null=True,
        blank=True,
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    gst_free = models.BooleanField(default=False)
    date_issued = models.DateTimeField(auto_now_add=True, null=False)
    date_updated = models.DateTimeField(auto_now=True, null=False)
    date_due = models.DateField(null=True, blank=False)
    proponent_reference_number = models.CharField(null=True, blank=True, max_length=50)

    # Fields that will match those in the ledger system
    order_number = models.CharField(unique=True, max_length=128, blank=False, null=True)
    basket_id = models.IntegerField(unique=True, blank=False, null=True)
    invoice_reference = models.CharField(
        unique=True, max_length=36, blank=False, null=True
    )

    # Why uuid? We need a unique identifier that is not
    # easily guessable for the ledger checkout callback api
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    # Not sure if we will need this, the invoice file may exist within ledger
    invoice_pdf = SecureFileField(
        upload_to=invoice_pdf_upload_path, null=True, blank=True
    )
    oracle_invoice_number = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        app_label = "leaseslicensing"
        ordering = ["-date_issued", "approval"]

    def __str__(self):
        return (
            f"Invoice: {self.lodgement_number} for Approval: {self.approval} "
            f"of Amount: {self.amount} with Status: {self.status}"
        )

    def user_has_object_permission(self, user_id):
        self.approval.user_has_object_permission(user_id)

    @property
    def balance(self):
        credit_debit_sums = self.transactions.aggregate(
            credit=Coalesce(models.Sum("credit"), Decimal("0.00")),
            debit=Coalesce(models.Sum("debit"), Decimal("0.00")),
        )
        balance = self.amount + credit_debit_sums["credit"] - credit_debit_sums["debit"]
        logger.debug(f"Balance for Invoice: {self} is {balance}")
        return Decimal(balance).quantize(Decimal("0.01"))

    @property
    def invoicing_details(self):
        return self.approval.current_proposal.invoicing_details


class InvoiceTransactionManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .annotate(
                cumulative_balance=Window(
                    expression=Sum("debit"),
                    order_by=F("datetime_created").asc(),
                )
                - Window(
                    expression=Sum("credit"),
                    order_by=F("datetime_created").asc(),
                )
            )
        )


class InvoiceTransaction(RevisionedMixin, models.Model):
    objects = InvoiceTransactionManager()
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.PROTECT,
        related_name="transactions",
        null=False,
        blank=False,
    )
    credit = models.DecimalField(
        max_digits=9, decimal_places=2, blank=False, null=False, default=Decimal("0.00")
    )
    debit = models.DecimalField(
        max_digits=9, decimal_places=2, blank=False, null=False, default=Decimal("0.00")
    )
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_updated = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "leaseslicensing"
        ordering = ["datetime_created"]

    def __str__(self):
        return f"Transaction: {self.id} for Invoice: {self.invoice} Credit: {self.credit}, Debit: {self.debit}"
