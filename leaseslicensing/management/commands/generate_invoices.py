import logging
from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from ledger_api_client import utils as ledger_api_client_utils

from leaseslicensing.components.approvals.models import Approval
from leaseslicensing.components.invoicing.models import Invoice, InvoicingAndReviewDates
from leaseslicensing.components.organisations.models import (
    Organisation,
    OrganisationContact,
)
from leaseslicensing.components.proposals.models import Proposal

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "This script is designed to run as a daily cron job and generate any invoices that need to be issued"

    def add_arguments(self, parser):
        parser.add_argument(
            "--test",
            action="store_true",
            help=(
                "Adding the test flag will process annual, quarterly and monthly invoices regardless of the date "
                "and will output what invoices would be generated without actually generating anything."
            ),
        )

    def handle(self, *args, **options):
        year = timezone.now().year
        date = timezone.now().date()
        month = timezone.now().month
        month_name = timezone.now().strftime("%B")
        day_of_month = timezone.now().day

        try:
            invoicing_and_review_dates = InvoicingAndReviewDates.objects.get(year=year)
        except InvoicingAndReviewDates.DoesNotExist:
            logger.error(f"Unable to retrieve InvoicingAndReviewDates for year: {year}")
            return

        approvals = Approval.objects.filter(
            status=Approval.APPROVAL_STATUS_CURRENT,
            current_proposal__processing_status=Proposal.PROCESSING_STATUS_APPROVED,
        ).exclude(
            current_proposal__invoicing_details__charge_method__key__in=[
                # No invoices need to be generated
                settings.CHARGE_METHOD_NO_RENT_OR_LICENCE_CHARGE,
                # No invoices need to be generated - Once off charge invoices are generated when the finance officer
                # completes editing invoicing for the application
                settings.CHARGE_METHOD_ONCE_OFF_CHARGE,
            ]
        )

        if options["test"]:
            logger.info("Running in test mode - no invoices will be generated")
            self.generate_annual_invoices(approvals, test=True)
            self.generate_quarterly_invoices(approvals, test=True)
            self.generate_monthly_invoices(approvals, test=True)
            return

        if date == invoicing_and_review_dates.invoicing_date_annually:
            logger.info(f"Today is the annual invoicing date for {year}.")
            self.generate_annual_invoices(approvals)

        if (
            month in [3, 6, 9, 12]
            and day_of_month == invoicing_and_review_dates.invoicing_day_for_quarter
        ):
            logger.info(
                f"Today is the quarterly invoicing date for the {month_name} quarter of {year}."
            )
            self.generate_quarterly_invoices(approvals)

        if day_of_month == invoicing_and_review_dates.invoicing_day_for_month:
            logger.info(
                f"Today is the monthly invoicing date for {month_name}, {year}."
            )
            self.generate_monthly_invoices(approvals)

    def generate_annual_invoices(self, approvals, test=False):
        annual_invoicing_approvals = approvals.filter(
            current_proposal__invoicing_details__invoicing_repetition_type__key=settings.REPETITION_TYPE_ANNUALLY
        )
        logger.info(
            f"\n\nFound {annual_invoicing_approvals.count()} approvals that need annual invoices generated.\n"
        )
        for approval in annual_invoicing_approvals:
            self.generate_invoice(approval, test=test)

    def generate_quarterly_invoices(self, approvals, test=False):
        quarterly_invoicing_approvals = approvals.filter(
            current_proposal__invoicing_details__invoicing_repetition_type__key=settings.REPETITION_TYPE_QUARTERLY
        )
        logger.info(
            f"\n\nFound {quarterly_invoicing_approvals.count()} approvals that need quarterly invoices generated.\n"
        )
        for approval in quarterly_invoicing_approvals:
            self.generate_invoice(approval, test=test)

    def generate_monthly_invoices(self, approvals, test=False):
        logger.info("\n\nGenerating monthly invoices\n")
        monthly_invoicing_approvals = approvals.filter(
            current_proposal__invoicing_details__invoicing_repetition_type__key=settings.REPETITION_TYPE_MONTHLY
        )
        logger.info(
            f"\n\nFound {monthly_invoicing_approvals.count()} approvals that need monthly invoices generated.\n"
        )
        for approval in monthly_invoicing_approvals:
            self.generate_invoice(approval, test=test)

    def generate_invoice(self, approval, test=False):
        if (
            not hasattr(approval.current_proposal, "invoicing_details")
            or approval.current_proposal.invoicing_details is None
        ):
            logger.warn(f"\n\nNo invoicing details found for Approval: {approval}")
            return

        invoicing_details = approval.current_proposal.invoicing_details
        invoice_amount = invoicing_details.invoice_amount()
        # Todo add the invoicing frequency to the description
        description = f"{approval.approval_type} {approval.lodgement_number}"
        inc_gst = True
        if "licence" in approval.approval_type.name.lower():
            inc_gst = False

        due_date = timezone.now().date() + timedelta(
            days=settings.DEFAULT_DAYS_BEFORE_PAYMENT_DUE
        )

        invoice = Invoice(
            approval=approval, amount=invoice_amount, inc_gst=inc_gst, date_due=due_date
        )

        if test:
            logger.info(f"\n\nTest mode - Invoice would be generated: {invoice}")
            return

        ledger_order_lines = []
        ledger_order_lines.append(
            {
                "ledger_description": description,
                "quantity": 1,
                "price_excl_tax": str(
                    invoice_amount
                ),  # Todo gst applies for leases but not for licences
                "price_incl_tax": str(invoice_amount),
                "oracle_code": "Todo: Get Oracle Code",
                "line_status": settings.LEDGER_DEFAULT_LINE_STATUS,
            },
        )

        request = ledger_api_client_utils.FakeRequestSessionObj()

        booking_reference = (
            f"{approval.approval_type} {approval.lodgement_number} "
            f"(Billing Cycle: {invoicing_details.invoicing_repetition_type.display_name})"
        )

        basket_params = {
            "products": ledger_order_lines,
            "vouchers": [],
            "system": settings.PAYMENT_SYSTEM_ID,
            "tax_override": True,
            "custom_basket": True,
            "booking_reference": str(booking_reference),
            "no_payment": True,
        }
        if type(approval.applicant) == Organisation:
            organisation = approval.applicant
            basket_params["organisation"] = organisation.ledger_organisation_id
            admin_contact = organisation.contacts.filter(
                user_role=OrganisationContact.USER_ROLE_CHOICE_ADMIN,
                user_status=OrganisationContact.USER_STATUS_CHOICE_ACTIVE,
            ).first()
            if not admin_contact:
                logger.error(
                    f"Unable to retrieve admin contact for organisation: {organisation}"
                )
                return

            request.user = admin_contact.user
        else:
            request.user = approval.applicant

        basket_hash = ledger_api_client_utils.create_basket_session(
            request, request.user.id, basket_params
        )
        basket_hash = basket_hash.split("|")[0]

        invoice_text = f"Leases Licensing Invoice {invoice.lodgement_number}"
        if approval.current_proposal.proponent_reference_number:
            invoice_text += f"(Proponent Ref: {approval.current_proposal.proponent_reference_number})"

        return_preload_url = (
            f"{settings.LEASES_LICENSING_EXTERNAL_URL}"
            f"/api/invoicing/ledger-api-invoice-success-callback/{invoice.uuid}"
        )

        future_invoice = ledger_api_client_utils.process_create_future_invoice(
            basket_hash, invoice_text, return_preload_url
        )

        logger.info(f"Future Invoice: {future_invoice}")

        if 200 != future_invoice["status"]:
            logger.error(
                f"Failed to create future Invoice {invoice.lodgement_number} with basket_hash "
                f"{basket_hash}, invoice_text {invoice_text}, return_preload_url {return_preload_url}"
            )
            return

        data = future_invoice["data"]

        invoice.order_number = data["order"]
        invoice.basket_id = data["basket_id"]
        invoice.invoice_reference = data["invoice"]

        invoice.save()

        self.stdout.write(
            self.style.SUCCESS(f"\tGenerated Invoice: {invoice.lodgement_number}\n")
        )
