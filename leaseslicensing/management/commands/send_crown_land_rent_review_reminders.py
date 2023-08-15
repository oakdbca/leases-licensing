import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from leaseslicensing.components.approvals.email import (
    send_approval_crown_land_rent_review_email_notification,
)
from leaseslicensing.components.approvals.models import Approval
from leaseslicensing.components.proposals.models import Proposal

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        "This script is designed to run as a daily cron job and send out reminders "
        "for any Crown Land Rent Reviews that are due"
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
        charge_method_in = "current_proposal__invoicing_details__charge_method__key__in"
        filters = {
            "status": Approval.APPROVAL_STATUS_CURRENT,
            "current_proposal__processing_status": Proposal.PROCESSING_STATUS_APPROVED,
            charge_method_in: settings.CHARGE_METHODS_REQUIRING_CROWN_LAND_RENT_REVIEW,
        }
        approvals = Approval.objects.filter(**filters)
        for approval in approvals:
            logger.debug(f"Checking approval: {approval}")
            months_due_in = None
            if approval.crown_land_rent_review_reminder_due_in(months=12):
                months_due_in = 12

            if approval.crown_land_rent_review_reminder_due_in(months=6):
                months_due_in = 6

            if approval.crown_land_rent_review_due_today:
                months_due_in = 0

            if months_due_in is not None:
                if options["test"]:
                    logger.debug(
                        f"Test: Would have sent crown land rent reivew reminder for approval: {approval}"
                    )
                    continue

                logger.info(
                    f"Sending crown land rent review reminder for approval: {approval}"
                )
                try:
                    send_approval_crown_land_rent_review_email_notification(
                        approval, months_due_in
                    )
                except Exception as e:
                    logger.error(
                        f"Error sending crown land rent review reminder for approval: {approval}: {e}"
                    )
                    continue
