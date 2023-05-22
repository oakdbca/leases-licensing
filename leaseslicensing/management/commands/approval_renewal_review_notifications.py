""" This command should be run as a daily cron job to send renewal notices for approvals
that are due to expire in x days (defined in settings.APPROVAL_RENEWAL_DAYS_PRIOR_TO_EXPIRY)  """

import logging
from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone

from leaseslicensing.components.approvals.email import (
    send_approval_renewal_review_email_notification,
)
from leaseslicensing.components.approvals.models import Approval

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        f"Send Approval renewal review notification to assessors when approval is due to expire in "
        f"{settings.APPROVAL_RENEWAL_DAYS_PRIOR_TO_EXPIRY} days"
    )

    def handle(self, *args, **options):
        errors = []
        updates = []
        today = timezone.localtime(timezone.now()).date()
        expiry_notification_date = today + timedelta(
            days=settings.APPROVAL_RENEWAL_DAYS_PRIOR_TO_EXPIRY
        )
        renewal_conditions = {
            "expiry_date__lte": expiry_notification_date,
            "renewal_review_notification_sent_to_assessors": False,
            "replaced_by__isnull": True,
        }
        logger.info(f"Running command {__name__}")
        approvals = Approval.objects.filter(
            Q(status="current") | Q(status="suspended")
        ).filter(**renewal_conditions)

        if not approvals or 0 == len(approvals):
            logger.info(
                "No approvals found that need renewal review notifications sent today."
            )
            return

        logger.info(f"{approvals}")
        for approval in approvals:
            try:
                send_approval_renewal_review_email_notification(approval)
                approval.renewal_review_notification_sent_to_assessors = True
                approval.status = (
                    Approval.APPROVAL_STATUS_CURRENT_PENDING_RENEWAL_REVIEW
                )
                approval.save()
                logger.info(
                    f"Renewal review notification sent for Approval {approval.id}"
                )
                updates.append(approval.lodgement_number)
            except Exception as e:
                err_msg = "Error sending renewal notice for Approval {}".format(
                    approval.lodgement_number
                )
                logger.error(f"{err_msg}\n{str(e)}")
                errors.append(err_msg)

        cmd_name = __name__.split(".")[-1].replace("_", " ").upper()
        err_str = (
            f'<strong style="color: red;">Errors: {len(errors)}</strong>'
            if len(errors) > 0
            else '<strong style="color: green;">Errors: 0</strong>'
        )
        msg = "<p>{} completed. Errors: {}. IDs updated: {}.</p>".format(
            cmd_name, err_str, updates
        )
        logger.info(msg)
        print(msg)  # will redirect to cron_tasks.log file, by the parent script
