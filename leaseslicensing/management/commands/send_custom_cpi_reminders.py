import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from leaseslicensing.components.approvals.email import (
    send_approval_custom_cpi_entry_email_notification,
)
from leaseslicensing.components.approvals.models import Approval
from leaseslicensing.components.proposals.models import Proposal

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    SIXTY = 60
    FORTY_FIVE = 45

    help = (
        f"This script is designed to run as a daily cron job and send out reminders "
        f"({SIXTY} days prior and {FORTY_FIVE} days prior) for any custom cpi figures that are due to be entered"
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
        charge_method_key = "current_proposal__invoicing_details__charge_method__key"
        filters = {
            "status": Approval.APPROVAL_STATUS_CURRENT,
            "current_proposal__processing_status": Proposal.PROCESSING_STATUS_APPROVED,
            charge_method_key: settings.CHARGE_METHOD_BASE_FEE_PLUS_ANNUAL_CPI_CUSTOM,
        }
        approvals = Approval.objects.filter(**filters)
        for approval in approvals:
            logger.debug(f"Checking approval: {approval}")
            days_due_in = None
            if approval.custom_cpi_entry_reminder_due_in(days=self.SIXTY):
                days_due_in = self.SIXTY

            if approval.crown_land_rent_review_reminder_due_in(days=self.FORTY_FIVE):
                days_due_in = self.FORTY_FIVE

            if days_due_in is not None:
                if options["test"]:
                    logger.debug(
                        f"Test: Would have sent custom cpi entry reminder for approval: {approval}"
                    )
                    continue

                logger.info(
                    f"Sending custom cpi entry reminder for approval: {approval}"
                )
                try:
                    send_approval_custom_cpi_entry_email_notification(
                        approval, days_due_in
                    )
                except Exception as e:
                    logger.error(
                        f"Error sending cpi entry reminder for approval: {approval}: {e}"
                    )
                    continue
