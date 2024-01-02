import logging
import time

from django.conf import settings
from django.core.management.base import BaseCommand

from leaseslicensing.components.approvals.email import (
    send_approval_custom_cpi_entry_email_notification,
)
from leaseslicensing.components.approvals.models import Approval
from leaseslicensing.components.proposals.models import Proposal

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    REMINDER_ONE = settings.CUSTOM_CPI_REMINDER_DAYS_PRIOR_TO_INVOICE_ISSUE_DATE[0]
    REMINDER_TWO = settings.CUSTOM_CPI_REMINDER_DAYS_PRIOR_TO_INVOICE_ISSUE_DATE[1]

    help = (
        f"This script is designed to run as a daily cron job and send out reminders ({REMINDER_ONE} days prior and "
        f"{REMINDER_TWO} days prior to the issue date for the next invoice) "
        "for any custom cpi figures that are due to be entered"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--test",
            action="store_true",
            help=(
                "Adding the test flag will list reminders without actually attempting to send any emails."
            ),
        )

    def handle(self, *args, **options):
        start = time.time()
        logger.info("Running send_custom_cpi_reminders management command")
        charge_method_key = "current_proposal__invoicing_details__charge_method__key"
        current_approval_statuses = [
            Approval.APPROVAL_STATUS_CURRENT,
            Approval.APPROVAL_STATUS_CURRENT_PENDING_RENEWAL_REVIEW,
            Approval.APPROVAL_STATUS_CURRENT_PENDING_RENEWAL,
        ]
        filters = {
            "status__in": current_approval_statuses,
            "current_proposal__processing_status": Proposal.PROCESSING_STATUS_APPROVED,
            charge_method_key: settings.CHARGE_METHOD_BASE_FEE_PLUS_ANNUAL_CPI_CUSTOM,
        }
        approvals = Approval.objects.filter(**filters)
        for approval in approvals:
            logger.info(f"Checking approval: {approval}")
            invoicing_details = approval.current_proposal.invoicing_details

            # Just in case
            if not invoicing_details.has_future_invoicing_periods:
                logger.debug(
                    f"Skipping approval: {approval} as it has no future invoicing periods"
                )
                continue

            if invoicing_details.custom_cpi_entered_for_next_invoicing_period:
                logger.debug(
                    f"Skipping approval: {approval} as the custom cpi for the next "
                    "invoicing period has already been entered"
                )
                continue

            days_before_issue_date = None

            if approval.has_invoice_issue_date_in(days=self.REMINDER_ONE):
                days_before_issue_date = self.REMINDER_ONE

            if approval.has_invoice_issue_date_in(days=self.REMINDER_TWO):
                days_before_issue_date = self.REMINDER_TWO

            if days_before_issue_date is not None:
                if options["test"]:
                    logger.info(
                        f"Test: Would have sent custom cpi entry reminder for approval: {approval}"
                    )
                    continue

                logger.info(
                    f"Sending custom cpi entry reminder for approval: {approval}"
                )
                try:
                    send_approval_custom_cpi_entry_email_notification(
                        approval, days_before_issue_date
                    )
                except Exception as e:
                    logger.error(
                        f"Error sending cpi entry reminder for approval: {approval}: {e}"
                    )
                    continue

        logger.info("Finished running send_custom_cpi_reminders management command")
        time_taken = f"{time.time() - start:.4f}"
        logger.info(f"Total time taken: {time_taken} seconds")
