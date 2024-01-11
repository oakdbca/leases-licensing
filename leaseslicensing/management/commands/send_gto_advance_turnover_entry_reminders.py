import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from leaseslicensing.components.approvals.email import (
    send_approval_gto_advance_turnover_entry_reminder_email_notification,
)
from leaseslicensing.components.approvals.models import Approval
from leaseslicensing.components.proposals.models import Proposal

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        "This script is designed to run as a daily cron job and send out reminders "
        "for any approvals that have gross turnover in advance invoicing and no turnover estimate "
        "or actual turnover has been entered for the system to calculate the invoice amount from"
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
        charge_method = "current_proposal__invoicing_details__charge_method__key"
        filters = {
            "status__in": Approval.CURRENT_APPROVAL_STATUSES,
            "current_proposal__processing_status": Proposal.PROCESSING_STATUS_APPROVED,
            charge_method: settings.CHARGE_METHOD_PERCENTAGE_OF_GROSS_TURNOVER_IN_ADVANCE,
        }
        reminders_sent = []
        approvals = Approval.objects.filter(**filters)
        for approval in approvals:
            for (
                days_prior
            ) in settings.PERCENTAGE_OF_GROSS_TURNOVER_REMINDERS_DAYS_PRIOR:
                if approval.invoicing_details.turnover_entry_reminder_required(
                    days_prior=days_prior
                ):
                    if options["test"]:
                        logger.info(
                            f"Test: Would have turnover entry reminder for approval: {approval}"
                        )
                        continue

                    logger.info(
                        f"Sending turnover entry reminder for approval: {approval}"
                    )
                    try:
                        send_approval_gto_advance_turnover_entry_reminder_email_notification(
                            approval, days_prior
                        )
                        reminders_sent.append(approval.lodgement_number)
                    except Exception as e:
                        logger.error(
                            f"Error sending turnover entry reminder for approval: {approval}: {e}"
                        )
                        continue

        if len(reminders_sent) > 0:
            logger.info(
                f"Turnover entry reminders sent for the following approvals: {reminders_sent}"
            )
        else:
            logger.info("No turnover entry reminders were required today.")
