import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from leaseslicensing.components.approvals.models import Approval
from leaseslicensing.components.invoicing.email import (
    send_new_invoice_raised_notification,
)
from leaseslicensing.components.invoicing.models import Invoice
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
        logger.info(f"Running command {__name__}")
        approvals = Approval.objects.filter(
            status=Approval.APPROVAL_STATUS_CURRENT,
            current_proposal__processing_status=Proposal.PROCESSING_STATUS_APPROVED,
        ).exclude(
            current_proposal__invoicing_details__charge_method__key__in=[
                # No invoices need to be generated
                settings.CHARGE_METHOD_NO_RENT_OR_LICENCE_CHARGE,
                # No invoices need to be generated - Once off charge invoices are generated when the finance officer
                # completes editing invoicing for the application when it is 'Approved - Editing Invoicing'
                settings.CHARGE_METHOD_ONCE_OFF_CHARGE,
                # No invoices need to be generated - Invoices are generated when the finance officer enters the
                # actual turnover amount for the approval
                settings.CHARGE_METHOD_PERCENTAGE_OF_GROSS_TURNOVER,
            ]
        )

        invoices_generated = []
        for approval in approvals:
            if (
                not hasattr(approval, "invoicing_details")
                or approval.invoicing_details is None
            ):
                logger.warn(f"\n\nNo invoicing details found for Approval: {approval}")
                return

            invoicing_details = approval.invoicing_details

            if not invoicing_details.has_future_invoicing_periods:
                logger.info(
                    f"Skipping Approval: {approval} - no future invoicing periods"
                )
                continue

            invoices_due_for_issue_today = (
                invoicing_details.invoices_due_for_issue_today
            )
            for invoice in invoices_due_for_issue_today:
                invoices_generated.apend(
                    self.generate_invoice(approval, invoice, test=options["test"])
                )

        logger.info(f"Generated the following invoices {invoices_generated}")
        logger.info(f"Finished running command {__name__}")

    @transaction.atomic
    def generate_invoice(self, approval, invoice, test=False):
        logger.info(f"\tGenerating Invoice from preview: {invoice}")
        invoice = Invoice(
            approval=approval,
            amount=invoice["amount_object"]["amount"],
            gst_free=approval.approval_type.gst_free,
        )

        if test:
            logger.info(
                f"Test mode - Invoice record would be generated: {invoice} (and finance group would be sent an email)"
            )
            return

        invoice.save()

        # send to the applicant and cc finance officer
        send_new_invoice_raised_notification(approval, invoice)

        logger.info(
            self.style.SUCCESS(f"\tGenerated Invoice: {invoice.lodgement_number}\n")
        )

        return invoice.lodgement_number
