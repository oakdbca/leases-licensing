import logging

from django.conf import settings
from django.urls import reverse

from leaseslicensing.components.emails.emails import TemplateEmailBase

logger = logging.getLogger(__name__)

SYSTEM_NAME = settings.SYSTEM_NAME_SHORT + " Automated Message"


def send_invoice_record_created_notification_email(request, approval, invoices):
    email = TemplateEmailBase(
        subject=f"New Invoice Record{ 's' if len(invoices)>1 else ''} Created for {approval.lodgement_number}",
        html_template="leaseslicensing/emails/invoicing/send_invoice_record_created_notification_email.html",
        txt_template="leaseslicensing/emails/invoicing/send_invoice_record_created_notification_email.txt",
    )
    url = request.build_absolute_uri(
        reverse(
            "internal-approval-detail",
            kwargs={"pk": approval.id},
        )
    )

    context = {
        "approval": approval,
        "invoices": invoices,
        "url": url,
    }
    recipients = [approval.submitter.email]
    email.send(
        recipients, cc=[settings.LEASING_FINANCE_NOTIFICATION_EMAIL], context=context
    )
    # sender = request.user if request else settings.DEFAULT_FROM_EMAIL
