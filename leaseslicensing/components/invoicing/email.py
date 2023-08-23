import logging

from django.conf import settings
from django.urls import reverse
from ledger_api_client.ledger_models import EmailUserRO as EmailUser

from leaseslicensing.components.approvals.email import (
    _log_approval_email,
    _log_org_email,
    _log_user_email,
)
from leaseslicensing.components.emails.emails import TemplateEmailBase
from leaseslicensing.helpers import emails_list_for_group
from leaseslicensing.ledger_api_utils import retrieve_dbca_ledger_organisation

logger = logging.getLogger(__name__)

SYSTEM_NAME = settings.SYSTEM_NAME_SHORT + " Automated Message"


def send_new_invoice_raised_notification(approval, invoice):
    email = TemplateEmailBase(
        subject=f"New Invoice Ready for {approval.approval_type} {approval.lodgement_number}",
        html_template="leaseslicensing/emails/invoicing/send_new_invoice_raised_notification.html",
        txt_template="leaseslicensing/emails/invoicing/send_new_invoice_raised_notification.txt",
    )

    external_invoices_url = settings.SITE_URL
    external_invoices_url += reverse("external-invoices")

    pay_now_url = settings.SITE_URL
    pay_now_url = reverse("external-pay-invoice", kwargs={"pk": invoice.id})

    context = {
        "approval": approval,
        "invoice": invoice,
        "external_invoices_url": external_invoices_url,
        "pay_now_url": pay_now_url,
    }
    proposal = approval.current_proposal
    recipients = proposal.applicant_emails
    finance_group_member_emails = emails_list_for_group(settings.GROUP_FINANCE)
    finance_group_member_emails.append(settings.LEASING_FINANCE_NOTIFICATION_EMAIL)
    msg = email.send(recipients, cc=finance_group_member_emails, context=context)

    sender = settings.DEFAULT_FROM_EMAIL
    sender_user = EmailUser.objects.get(email=sender)

    if approval.current_proposal.org_applicant:
        _log_org_email(
            msg,
            approval.current_proposal.org_applicant,
            proposal.submitter,
            sender=sender_user,
        )
    else:
        _log_user_email(msg, approval.submitter, proposal.submitter, sender=sender_user)

    _log_approval_email(msg, approval, sender=sender_user)


def send_new_invoice_raised_internal_notification(approval, invoice):
    email = TemplateEmailBase(
        subject=f"New Invoice Record Generated for {approval.approval_type} {approval.lodgement_number}",
        html_template="leaseslicensing/emails/invoicing/send_new_invoice_raised_internal_notification.html",
        txt_template="leaseslicensing/emails/invoicing/send_new_invoice_raised_internal_notification.txt",
    )
    internal_invoices = reverse(
        "internal-invoices",
    )
    internal_invoices_url = (
        f"{settings.LEASES_LICENSING_EXTERNAL_URL}{internal_invoices}"
    )

    context = {
        "approval": approval,
        "invoice": invoice,
        "internal_invoices_url": internal_invoices_url,
    }

    finance_group_member_emails = emails_list_for_group(settings.GROUP_FINANCE)
    msg = email.send(
        finance_group_member_emails,
        cc=[settings.LEASING_FINANCE_NOTIFICATION_EMAIL],
        context=context,
    )

    sender = settings.DEFAULT_FROM_EMAIL
    sender_user = EmailUser.objects.get(email=sender)

    _log_approval_email(msg, approval, sender=sender_user)


def send_invoice_paid_internal_notification(invoice):
    approval = invoice.approval
    email = TemplateEmailBase(
        subject=(
            f"Invoice {invoice.lodgement_number} for {approval.approval_type} "
            f"{approval.lodgement_number} has been Paid"
        ),
        html_template="leaseslicensing/emails/invoicing/send_invoice_paid_internal_notification.html",
        txt_template="leaseslicensing/emails/invoicing/send_invoice_paid_internal_notification.txt",
    )
    internal_invoices = reverse(
        "internal-invoices",
    )
    internal_invoices_url = (
        f"{settings.LEASES_LICENSING_EXTERNAL_URL}{internal_invoices}"
    )

    context = {
        "invoice": invoice,
        "internal_invoices_url": internal_invoices_url,
    }

    finance_group_member_emails = emails_list_for_group(settings.GROUP_FINANCE)
    msg = email.send(
        finance_group_member_emails,
        cc=[settings.LEASING_FINANCE_NOTIFICATION_EMAIL],
        context=context,
    )

    sender = settings.DEFAULT_FROM_EMAIL
    sender_user = EmailUser.objects.get(email=sender)

    _log_approval_email(msg, approval, sender=sender_user)


def send_invoice_paid_external_notification(invoice):
    approval = invoice.approval
    email = TemplateEmailBase(
        subject=(
            f"Payment Received for Invoice {invoice.lodgement_number} "
            f"({approval.approval_type} {approval.lodgement_number})"
        ),
        html_template="leaseslicensing/emails/invoicing/send_invoice_paid_external_notification.html",
        txt_template="leaseslicensing/emails/invoicing/send_invoice_paid_external_notification.txt",
    )
    external_invoices_url = reverse(
        "external-invoices",
    )
    external_invoices_url = (
        f"{settings.LEASES_LICENSING_EXTERNAL_URL}{external_invoices_url}"
    )

    dbca_ledger_organisation = retrieve_dbca_ledger_organisation()

    context = {
        "invoice": invoice,
        "approval": approval,
        "dbca": dbca_ledger_organisation,
        "settings": settings,
        "external_invoices_url": external_invoices_url,
    }

    finance_group_member_emails = emails_list_for_group(settings.GROUP_FINANCE)
    msg = email.send(
        finance_group_member_emails,
        cc=[settings.LEASING_FINANCE_NOTIFICATION_EMAIL],
        context=context,
    )

    sender = settings.DEFAULT_FROM_EMAIL
    sender_user = EmailUser.objects.get(email=sender)

    _log_approval_email(msg, approval, sender=sender_user)
