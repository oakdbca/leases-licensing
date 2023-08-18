import datetime
import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import F, Q
from django.utils import timezone
from ledger_api_client.ledger_models import EmailUserRO as EmailUser

from leaseslicensing.components.approvals.models import Approval
from leaseslicensing.components.compliances.models import (
    Compliance,
    ComplianceUserAction,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Change the status of Compliances from future to due when they are close to due date"

    def handle(self, *args, **options):
        today = timezone.localtime(timezone.now()).date()
        due_soon = today + datetime.timedelta(days=14)
        user = EmailUser.objects.get(email=settings.CRON_EMAIL)

        logger.info(f"Running command {__name__}")
        errors = []
        updates = []
        # update future compliances to due if they are close to due date
        compliances_due = Compliance.objects.filter(
            Q(due_date__lte=due_soon),
            Q(due_date__lte=F("approval__expiry_date")),
            approval__status=Approval.APPROVAL_STATUS_CURRENT,
            customer_status__in=[
                Compliance.CUSTOMER_STATUS_FUTURE,
                Compliance.CUSTOMER_STATUS_DUE,
            ],
        )
        for c in compliances_due:
            updated = False
            if (
                c.due_date <= today
                and c.customer_status != Compliance.CUSTOMER_STATUS_OVERDUE
            ):
                c.processing_status = Compliance.PROCESSING_STATUS_OVERDUE
                c.customer_status = Compliance.CUSTOMER_STATUS_OVERDUE
                updated = True

            elif (
                c.due_date <= due_soon
                and c.customer_status != Compliance.CUSTOMER_STATUS_DUE
            ):
                c.processing_status = Compliance.PROCESSING_STATUS_DUE
                c.customer_status = Compliance.CUSTOMER_STATUS_DUE
                updated = True

            if not updated:
                continue

            try:
                c.save()
                ComplianceUserAction.log_action(
                    c, ComplianceUserAction.ACTION_STATUS_CHANGE.format(c.id), user.id
                )
                logger.info(
                    "updated Compliance {} status to {}".format(
                        c.lodgement_number, c.processing_status
                    )
                )
                updates.append(c.lodgement_number)
            except Exception as e:
                err_msg = "Error updating Compliance {} status".format(
                    c.lodgement_number
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
