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

from leaseslicensing.components.invoicing import utils
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
    invoicing_day_of_month = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(28),
        ],
        help_text="Day of the month to generate invoices.",
        null=True,
        blank=True,
    )
    invoicing_month_of_year = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(12),
        ],
        help_text="Month of the year to generate invoices.",
        null=True,
        blank=True,
    )
    # Used to support legacy leases/licenses that have an unusual quarterly invoicing cycle
    # Can be 1, 2 or 3. 1 = [JAN, APR, JUL, OCT], 2 = [FEB, MAY, AUG, NOV], 3 = [MAR, JUN, SEP, DEC]
    invoicing_quarters_start_month = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        default=3,
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
        return f"Invoicing Details for Approval: {self.approval} (Current Proposal: {self.approval.current_proposal})"

    @property
    def approval(self):
        if not hasattr(self, "proposal") or not self.proposal:
            return None
        if not hasattr(self.proposal, "approval") or not self.proposal.approval:
            return None

        return self.proposal.approval

    def base_fee_plus_cpi(self):
        if not self.cpi_calculation_method:
            logger.warn(
                f"No CPI calculation method set for Invoicing Details: {self.id}"
            )
            return self.base_fee_amount

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

        return Decimal(self.base_fee_amount * (1 + cpi_value / 100)).quantize(
            Decimal("0.01")
        )

    @property
    def total_invoice_count(self):
        return len(self.invoicing_periods)

    @property
    def invoices_created(self):
        return (
            Invoice.objects.filter(invoicing_details=self)
            .exclude(status=Invoice.INVOICE_STATUS_VOID)
            .count()
        )

    @property
    def invoices_yet_to_be_generated(self):
        return self.total_invoice_count - self.invoices_created

    @property
    def invoicing_periods(self):
        """Returns an array of invoicing periods based on the invoicing details object"""
        invoicing_periods = []
        start_date = self.approval.start_date
        expiry_date = self.approval.expiry_date
        end_of_next_interval = self.get_end_of_next_interval(start_date)
        while end_of_next_interval <= expiry_date:
            delta = end_of_next_interval - start_date
            days = delta.days + 1  # The plus one to include the expiry day
            label = (
                f"{start_date.strftime('%d/%m/%Y')} to "
                f"{end_of_next_interval.strftime('%d/%m/%Y')} ({days} days)"
            )
            invoicing_periods.append(
                {
                    "label": label,
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_of_next_interval.strftime("%Y-%m-%d"),
                    "days": days,
                }
            )
            start_date = end_of_next_interval + relativedelta(days=1)
            end_of_next_interval = self.get_end_of_next_interval(start_date)

        # Check if a final period is required
        if start_date < expiry_date:
            delta = expiry_date - start_date
            days = delta.days + 1  # The plus one to include the expiry day
            invoicing_periods.append(
                {
                    "label": f"{start_date.strftime('%d/%m/%Y')} to {expiry_date.strftime('%d/%m/%Y')} ({days} days)",
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": expiry_date.strftime("%Y-%m-%d"),
                    "days": days,
                }
            )

        return invoicing_periods

    @property
    def invoicing_periods_start_dates(self):
        return [
            datetime.strptime(period["start_date"], "%Y-%m-%d").date()
            for period in self.invoicing_periods
        ]

    def preview_invoices(self, show_past_invoices=False):
        """
        Returns a preview array of invoices based on the invoicing periods for the invoicing details object
        By default it will only return invoices for future periods because we can fetch a list of past invoices
        from the database.
        """
        invoices = []
        first_issue_date = self.get_first_issue_date()
        days_running_total = 0
        amount_running_total = Decimal("0.00")
        issue_date = first_issue_date
        for i, invoicing_period in enumerate(self.invoicing_periods):
            # Net 30 payment terms
            due_date = issue_date + relativedelta(days=30)
            days_running_total += invoicing_period["days"]
            amount_object = self.get_amount_for_invoice(
                issue_date, invoicing_period["end_date"], invoicing_period["days"], i
            )
            amount_running_total = amount_running_total + amount_object["amount"]
            invoices.append(
                {
                    "number": i + 1,
                    "issue_date": self.get_issue_date(
                        issue_date, invoicing_period["end_date"]
                    ),
                    "due_date": self.get_due_date(due_date),
                    "time_period": invoicing_period["label"],
                    "amount_object": amount_object,
                    "days": invoicing_period["days"],
                    "days_running_total": days_running_total,
                    "amount_running_total": amount_running_total,
                    "hide": not show_past_invoices
                    and issue_date < timezone.now().date(),
                }
            )
            if i < len(self.invoicing_periods) - 1:
                issue_date = self.add_repetition_interval(issue_date)
            else:
                # The last issue date is the day after the expiry date for the approval
                issue_date = self.approval.expiry_date + relativedelta(days=1)

        return invoices

    def get_first_issue_date(self):
        start_date = self.approval.start_date

        if (
            self.charge_method.key
            != settings.CHARGE_METHOD_PERCENTAGE_OF_GROSS_TURNOVER
        ):
            first_issue_date = self.get_end_of_next_interval_sequential_year(
                start_date
            ) + relativedelta(days=1)
            if (
                self.invoicing_repetition_type.key == settings.REPETITION_TYPE_ANNUALLY
                and self.invoicing_month_of_year
            ):
                first_issue_date = first_issue_date.replace(
                    month=self.invoicing_month_of_year
                )
            if self.invoicing_day_of_month:
                first_issue_date = first_issue_date.replace(
                    day=self.invoicing_day_of_month
                )
            end_of_first_interval = self.invoicing_periods[0]["end_date"]
            if (
                first_issue_date
                <= datetime.strptime(end_of_first_interval, "%Y-%m-%d").date()
            ):
                first_issue_date = self.get_end_of_next_interval_sequential_year(
                    first_issue_date
                ) + relativedelta(days=1)
            return first_issue_date

        first_issue_date = start_date
        if self.invoicing_month_of_year:
            first_issue_date.replace(month=self.invoicing_month_of_year)
        if self.invoicing_day_of_month:
            first_issue_date.replace(day=self.invoicing_day_of_month)

        # This works for quarterly invoicing
        today = timezone.now().date()
        if settings.REPETITION_TYPE_QUARTERLY == self.invoicing_repetition_type.key:
            first_issue_date = start_date
            while first_issue_date < today:
                first_issue_date = self.get_end_of_next_financial_quarter(
                    first_issue_date
                ) + relativedelta(days=1)
            return first_issue_date.replace(day=self.invoicing_day_of_month)

        # This works for annual and monthly invoicing
        while first_issue_date < today:
            first_issue_date = self.addRepetitionInterval(first_issue_date)

        return first_issue_date

    def get_issue_date(self, issue_date, end_date):
        if (
            self.charge_method.key
            == settings.CHARGE_METHOD_PERCENTAGE_OF_GROSS_TURNOVER
        ):
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
            q = utils.financial_quarter_from_date(end_date)
            financial_year = f"{issue_date.year - 1}-{issue_date.year}"
            return f"On receipt of Q{q} {financial_year} financial statement"

        return issue_date.strftime("%d/%m/%Y")

    def get_due_date(self, due_date):
        if (
            self.charge_method.key
            == settings.CHARGE_METHOD_PERCENTAGE_OF_GROSS_TURNOVER
        ):
            return "30 Days after issue"
        return due_date.strftime("%d/%m/%Y")

    def get_year_sequence_index(self, index):
        if self.invoicing_repetition_type.key == settings.REPETITION_TYPE_ANNUALLY:
            return index
        if self.invoicing_repetition_type.key == settings.REPETITION_TYPE_QUARTERLY:
            return math.floor(index / 4)
        if self.invoicing_repetition_type.key == settings.REPETITION_TYPE_MONTHLY:
            return math.floor(index / self.invoicing_once_every)

    def get_amount_for_invoice(self, issue_date, end_date, days, index):
        amount_object = {
            "prefix": "$",
            "amount": Decimal("0.00"),
            "suffix": "",
        }
        if self.charge_method.key == settings.CHARGE_METHOD_ONCE_OFF_CHARGE:
            raise Exception(
                "To get the amount for a once off charge, simply access the once_off_charge_amount field"
            )

        if (
            self.charge_method.key
            == settings.CHARGE_METHOD_PERCENTAGE_OF_GROSS_TURNOVER
        ):
            return self.get_amount_for_gross_turnover_invoice(end_date, amount_object)
        if not self.base_fee_amount or self.base_fee_amount == Decimal("0.00"):
            return amount_object

        base_fee_amount = self.base_fee_amount

        # Ignore extra day in leap year so base fee is consistent
        if days == 366:
            days = 365

        # Caculate the base fee for this period i.e. days of period * cost per day
        base_fee_amount = days * (base_fee_amount / 365)

        if self.charge_method.key == settings.CHARGE_METHOD_BASE_FEE_PLUS_ANNUAL_CPI:
            amount_object["amount"] = base_fee_amount
            amount_object["suffix"] = " + CPI (ABS)"

        year_sequence_index = self.get_year_sequence_index(index)
        if (
            self.charge_method.key
            == settings.CHARGE_METHOD_BASE_FEE_PLUS_ANNUAL_CPI_CUSTOM
        ):
            amount_object["amount"] = base_fee_amount
            try:
                custom_cpi_year = self.custom_cpi_years.all()[year_sequence_index]
            except IndexError:
                logger.warning(
                    f"Invoicing Details: {self.id} - No custom CPI year for index "
                    f"{year_sequence_index}. Using base fee amount."
                )
            if custom_cpi_year and custom_cpi_year.percentage > Decimal("0.00"):
                amount_object["amount"] = Decimal(
                    base_fee_amount * (1 + custom_cpi_year.percentage / 100)
                ).quantize(Decimal("0.01"))
            else:
                amount_object["suffix"] = " + CPI (CUSTOM)"

        if (
            self.charge_method.key
            == settings.CHARGE_METHOD_BASE_FEE_PLUS_FIXED_ANNUAL_PERCENTAGE
        ):
            percentage = Decimal("0.00")
            suffix = (
                f"Enter percentage for year {year_sequence_index + 1}"
                if year_sequence_index > 0
                else ""
            )
            if year_sequence_index > 0:
                try:
                    annual_increment_percentage = (
                        self.annual_increment_percentages.all()[year_sequence_index - 1]
                    )
                    percentage = annual_increment_percentage.increment_percentage
                    base_fee_amount = base_fee_amount * (1 + percentage / 100)
                    suffix = ""
                except IndexError:
                    logger.warning(
                        f"Invoicing Details: {self.id} - No annual increment percentage for index "
                        f"{index}. Using base fee amount."
                    )

            amount_object["amount"] = Decimal(base_fee_amount).quantize(Decimal("0.01"))
            amount_object["suffix"] = suffix

        if (
            self.charge_method.key
            == settings.CHARGE_METHOD_BASE_FEE_PLUS_FIXED_ANNUAL_INCREMENT
        ):
            increment_amount = Decimal("0.00")
            suffix = (
                f"Enter increment amount for year {year_sequence_index + 1}"
                if year_sequence_index > 0
                else ""
            )
            annual_increment_amount = self.invoicingDetails.annual_increment_amounts[
                year_sequence_index - 1
            ]
            if annual_increment_amount:
                if annual_increment_amount.increment_amount:
                    increment_amount = annual_increment_amount.increment_amount
                base_fee_amount = base_fee_amount + increment_amount
                suffix = ""

            amount_object["amount"] = Decimal(base_fee_amount).quantize(Decimal("0.01"))
            amount_object["suffix"] = suffix

        return amount_object

    def get_amount_for_gross_turnover_invoice(self, end_date, amount_object):
        amount_object["prefix"] = ""
        amount_object["amount"] = Decimal("0.00")
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        financial_year = utils.financial_year_from_date(end_date)
        year = int(financial_year.split("-")[1])
        gross_turnover_percentage = next(
            (x for x in self.gross_turnover_percentages.all() if x.year == year), None
        )
        if not gross_turnover_percentage:
            amount_object["suffix"] = "???"
            return amount_object

        amount_object[
            "suffix"
        ] = f"{gross_turnover_percentage.percentage}% of Gross Turnover"
        return amount_object

    def get_end_of_next_interval(self, start_date):
        if (
            self.charge_method.key
            == settings.CHARGE_METHOD_PERCENTAGE_OF_GROSS_TURNOVER
        ):
            return self.get_end_of_next_interval_gross_turnover(start_date)

        # All other charge methods are based around each year of the duration of the lease/license
        # Which is being referred to as 'sequential year'
        return self.get_end_of_next_interval_sequential_year(start_date)

    def get_end_of_next_interval_sequential_year(self, start_date):
        if settings.REPETITION_TYPE_ANNUALLY == self.invoicing_repetition_type.key:
            return start_date + relativedelta(years=1) - relativedelta(days=1)

        if settings.REPETITION_TYPE_QUARTERLY == self.invoicing_repetition_type.key:
            return start_date + relativedelta(months=3) - relativedelta(days=1)

        if settings.REPETITION_TYPE_MONTHLY == self.invoicing_repetition_type.key:
            return (
                start_date
                + relativedelta(months=self.invoicing_once_every)
                - relativedelta(days=1)
            )

    def get_end_of_next_interval_gross_turnover(self, start_date):
        if settings.REPETITION_TYPE_ANNUALLY == self.invoicing_repetition_type.key:
            return utils.end_of_next_financial_year(start_date)

        if settings.REPETITION_TYPE_QUARTERLY == self.invoicing_repetition_type.key:
            return utils.end_of_next_financial_quarter(
                start_date, self.invoicing_quarters_start_month
            )

        if settings.REPETITION_TYPE_MONTHLY == self.invoicing_repetition_type.key:
            return utils.end_of_month(start_date)

    def get_end_of_next_financial_quarter(self, start_date):
        quarters = utils.quarters_from_start_month(self.invoicing_quarters_start_month)
        for quarter in quarters:
            end_of_financial_quarter = utils.end_of_next_financial_quarter(start_date)

            if start_date < end_of_financial_quarter:
                return end_of_financial_quarter

        # None of the four quarters were after the start date, so use the first quarter of the next year
        return start_date.replace(month=quarters[0] + 1) + relativedelta(years=1)

    def add_repetition_interval(self, issue_date):
        if self.invoicing_repetition_type.key == settings.REPETITION_TYPE_ANNUALLY:
            return issue_date + relativedelta(years=1)
        if self.invoicing_repetition_type.key == settings.REPETITION_TYPE_QUARTERLY:
            return issue_date + relativedelta(months=3)
        if self.invoicing_repetition_type.key == settings.REPETITION_TYPE_MONTHLY:
            return issue_date + relativedelta(months=1)

    @property
    def custom_cpi_entered_for_next_period(self):
        if (
            self.charge_method.key
            != settings.CHARGE_METHOD_BASE_FEE_PLUS_ANNUAL_CPI_CUSTOM
        ):
            logger.warning(
                f"custom_cpi_entered_for_next_period called for Invoicing Details: {self.id} "
                "which is not using custom CPI charge method."
            )
            return True  # So that no reminders would attempt to be sent


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

    def __str__(self):
        return f"Year: {self.year}, Increment Amount: {self.increment_amount}"

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

    def __str__(self):
        return f"Year: {self.year}, Increment Percentage: {self.increment_percentage}"

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


class FinancialQuarter(BaseModel):
    year = models.ForeignKey(
        PercentageOfGrossTurnover,
        on_delete=models.CASCADE,
        related_name="quarters",
    )
    quarter = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(4)]
    )
    gross_turnover = models.DecimalField(
        null=True, blank=True, max_digits=10, decimal_places=2
    )

    class Meta:
        app_label = "leaseslicensing"
        ordering = [
            "year",
            "quarter",
        ]

    def __str__(self):
        return f"Q{self.quarter} {self.year}: Gross Turnover: {self.gross_turnover or 'Not yet entered'}"


class CustomCPIYear(BaseModel):
    year = models.PositiveSmallIntegerField()
    label = models.CharField(max_length=100, null=True, blank=True)
    percentage = models.DecimalField(
        max_digits=4, decimal_places=1, default="0.0", null=True, blank=True
    )
    invoicing_details = models.ForeignKey(
        InvoicingDetails,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="custom_cpi_years",
    )

    class Meta:
        app_label = "leaseslicensing"
        ordering = ["invoicing_details", "year"]

    def __str__(self):
        return f"{self.year}: {self.percentage}%"


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

    INVOICE_STATUS_PENDING_UPLOAD_ORACLE_INVOICE = "pending_upload_oracle_invoice"
    INVOICE_STATUS_UNPAID = "unpaid"
    INVOICE_STATUS_PAID = "paid"
    INVOICE_STATUS_VOID = "void"
    INVOICE_STATUS_CHOICES = (
        (
            INVOICE_STATUS_PENDING_UPLOAD_ORACLE_INVOICE,
            "Pending Upload of Oracle Invoice",
        ),
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
        default=INVOICE_STATUS_PENDING_UPLOAD_ORACLE_INVOICE,
        null=True,
        blank=True,
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    gst_free = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True, null=False)
    date_updated = models.DateTimeField(auto_now=True, null=False)
    date_issued = models.DateTimeField(null=True, blank=False)
    date_due = models.DateTimeField(null=True, blank=False)
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
        return self.approval.user_has_object_permission(user_id)

    @property
    def balance(self):
        credit_debit_sums = self.transactions.aggregate(
            credit=Coalesce(models.Sum("credit"), Decimal("0.00")),
            debit=Coalesce(models.Sum("debit"), Decimal("0.00")),
        )
        balance = self.amount + credit_debit_sums["credit"] - credit_debit_sums["debit"]
        return Decimal(balance).quantize(Decimal("0.01"))

    @property
    def invoicing_details(self):
        return self.approval.current_proposal.invoicing_details

    @property
    def ledger_invoice_url(self):
        if not self.invoice_reference:
            return None
        return (
            settings.LEDGER_API_URL
            + "/ledgergw/invoice-pdf/"
            + settings.LEDGER_API_KEY
            + "/"
            + self.invoice_reference
        )


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
