import logging

from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.utils.encoding import smart_text

from leaseslicensing.components.bookings.confirmation_pdf import (
    create_confirmation_pdf_bytes,
)
from leaseslicensing.components.bookings.invoice_compliance_pdf import (
    create_invoice_compliance_pdf_bytes,
)
from leaseslicensing.components.bookings.invoice_pdf import create_invoice_pdf_bytes
from leaseslicensing.components.bookings.models import Booking
from leaseslicensing.components.bookings.monthly_confirmation_pdf import (
    create_monthly_confirmation_pdf_bytes,
)
from leaseslicensing.components.emails.emails import TemplateEmailBase

logger = logging.getLogger(__name__)

SYSTEM_NAME = settings.SYSTEM_NAME_SHORT + " Automated Message"


class ComplianceFeeInvoiceEventsSendNotificationEmail(TemplateEmailBase):
    def __init__(self):
        super().__init__()
        self.subject = "Your compliance fee invoice."
        self.html_template = "leaseslicensing/emails/bookings/events/send_compliance_fee_notification.html"
        self.txt_template = "leaseslicensing/emails/bookings/events/send_compliance_fee_notification.txt"


class ApplicationInvoiceFilmingSendNotificationEmail(TemplateEmailBase):
    def __init__(self):
        super().__init__()
        self.subject = "Your filming fee invoice."
        self.html_template = (
            "leaseslicensing/emails/bookings/filming/send_filming_fee_notification.html"
        )
        self.txt_template = (
            "leaseslicensing/emails/bookings/filmig/send_filming_fee_notification.txt"
        )


class ApplicationFeeInvoiceTClassSendNotificationEmail(TemplateEmailBase):
    def __init__(self):
        super().__init__()
        self.subject = "Your application fee invoice."
        self.html_template = "leaseslicensing/emails/bookings/tclass/send_application_fee_notification.html"
        self.txt_template = "leaseslicensing/emails/bookings/tclass/send_application_fee_notification.txt"


class ApplicationFeeConfirmationTClassSendNotificationEmail(TemplateEmailBase):
    def __init__(self):
        super().__init__()
        self.subject = "Your application fee confirmation."
        self.html_template = (
            "leaseslicensing/emails/bookings/tclass/"
            + "send_application_fee_confirmation_notification.html"
        )
        self.txt_template = (
            "leaseslicensing/emails/bookings/tclass/"
            + "send_application_fee_confirmation_notification.txt"
        )


class InvoiceTClassSendNotificationEmail(TemplateEmailBase):
    def __init__(self):
        super().__init__()
        self.subject = "Your booking invoice."
        self.html_template = (
            "leaseslicensing/emails/bookings/tclass/send_invoice_notification.html"
        )
        self.txt_template = (
            "leaseslicensing/emails/bookings/tclass/send_invoice_notification.txt"
        )


class MonthlyInvoiceTClassSendNotificationEmail(TemplateEmailBase):
    def __init__(self):
        super().__init__()
        self.subject = "Your monthly booking invoice."
        self.html_template = "leaseslicensing/emails/bookings/tclass/send_monthly_invoice_notification.html"
        self.txt_template = "leaseslicensing/emails/bookings/tclass/send_monthly_invoice_notification.txt"


class ConfirmationTClassSendNotificationEmail(TemplateEmailBase):
    def __init__(self):
        super().__init__()
        self.subject = "Your booking confirmation."
        self.html_template = (
            "leaseslicensing/emails/bookings/tclass/send_confirmation_notification.html"
        )
        self.txt_template = (
            "leaseslicensing/emails/bookings/tclass/send_confirmation_notification.txt"
        )


class MonthlyInvoicesFailedTClassEmail(TemplateEmailBase):
    def __init__(self):
        super().__init__()
        self.subject = "Failed: COLS Monthly Invoices."
        self.html_template = "leaseslicensing/emails/bookings/tclass/send_monthly_invoices_failed_notification.html"
        self.txt_template = "leaseslicensing/emails/bookings/tclass/send_monthly_invoices_failed_notification.txt"


class SendPaymentDueNotificationTClassEmail(TemplateEmailBase):
    def __init__(self):
        super().__init__()
        self.subject = "COLS Monthly/BPAY Bookings Invoices Overdue."
        self.html_template = (
            "leaseslicensing/emails/bookings/tclass/send_payment_due_notification.html"
        )
        self.txt_template = (
            "leaseslicensing/emails/bookings/tclass/send_payment_due_notification.txt"
        )


class SendExternalPaymentDueNotificationTClassEmail(TemplateEmailBase):
    def __init__(self):
        super().__init__()
        self.subject = "Your booking invoice is overdue."
        self.html_template = "leaseslicensing/emails/bookings/tclass/send_external_payment_due_notification.html"
        self.txt_template = "leaseslicensing/emails/bookings/tclass/send_external_payment_due_notification.txt"


class PaymentDueNotificationFailedTClassEmail(TemplateEmailBase):
    def __init__(self):
        super().__init__()
        self.subject = "Failed: COLS Payment Due Notifications"
        self.html_template = "leaseslicensing/emails/bookings/tclass/send_external_payment_due_notification_failed.html"
        self.txt_template = "leaseslicensing/emails/bookings/tclass/send_external_payment_due_notification_failed.txt"


# def send_application_awaiting_payment_invoice_filming_email_notification
# (request, proposal, recipients, is_test=False):
#    email = ApplicationAwaitingPaymentInvoiceFilmingSendNotificationEmail()
#    #url = request.build_absolute_uri(reverse('external-proposal-detail',kwargs={'proposal_pk': proposal.id}))
#
#    context = {
#        'proposal_lodgement_number': proposal.lodgement_number,
#        # 'url': url,
#    }
#
#    filename = 'awaiting_payment_invoice.pdf'
#    doc = create_awaiting_payment_invoice_pdf_bytes(filename, proposal)
#    attachment = (filename, doc, 'application/pdf')
#
#    msg = email.send(recipients, attachments=[attachment], context=context)
#    if is_test:
#        return
#
#    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
#    _log_proposal_email(msg, proposal, sender=sender)
#    if proposal.org_applicant:
#        _log_org_email(msg, proposal.org_applicant, proposal.submitter, sender=sender)
#    else:
#        _log_user_email(msg, proposal.submitter, proposal.submitter, sender=sender)


def send_application_invoice_filming_email_notification(
    request, proposal, invoice, recipients, is_test=False
):
    email = ApplicationInvoiceFilmingSendNotificationEmail()
    # url = request.build_absolute_uri(reverse('external-proposal-detail',kwargs={'proposal_pk': proposal.id}))

    context = {
        "proposal_lodgement_number": proposal.lodgement_number,
        # 'url': url,
    }

    filename = "invoice.pdf"
    doc = create_invoice_pdf_bytes(filename, invoice, proposal)
    attachment = (filename, doc, "application/pdf")

    msg = email.send(recipients, attachments=[attachment], context=context)
    if is_test:
        return

    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_proposal_email(msg, proposal, sender=sender)
    if proposal.org_applicant:
        _log_org_email(msg, proposal.org_applicant, proposal.submitter, sender=sender)
    else:
        _log_user_email(msg, proposal.submitter, proposal.submitter, sender=sender)


def send_compliance_fee_invoice_events_email_notification(
    request, compliance, invoice, recipients, is_test=False
):
    email = ComplianceFeeInvoiceEventsSendNotificationEmail()
    # url = request.build_absolute_uri(reverse('external-proposal-detail',kwargs={'proposal_pk': proposal.id}))

    context = {
        "proposal_lodgement_number": compliance.proposal.lodgement_number,
        "compliance_lodgement_number": compliance.lodgement_number,
        # 'url': url,
    }

    filename = "invoice.pdf"
    doc = create_invoice_compliance_pdf_bytes(filename, invoice, compliance)
    attachment = (filename, doc, "application/pdf")

    msg = email.send(recipients, attachments=[attachment], context=context)
    if is_test:
        return

    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_proposal_email(msg, compliance.proposal, sender=sender)
    if compliance.proposal.org_applicant:
        _log_org_email(
            msg, compliance.proposal.org_applicant, compliance.submitter, sender=sender
        )
    else:
        _log_user_email(
            msg, compliance.proposal.submitter, compliance.submitter, sender=sender
        )


def send_application_fee_invoice_tclass_email_notification(
    request, proposal, invoice, recipients, is_test=False
):
    email = ApplicationFeeInvoiceTClassSendNotificationEmail()
    # url = request.build_absolute_uri(reverse('external-proposal-detail',kwargs={'proposal_pk': proposal.id}))

    context = {
        "lodgement_number": proposal.lodgement_number,
        # 'url': url,
    }

    filename = "invoice.pdf"
    doc = create_invoice_pdf_bytes(filename, invoice, proposal)
    attachment = (filename, doc, "application/pdf")

    msg = email.send(recipients, attachments=[attachment], context=context)
    if is_test:
        return

    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_proposal_email(msg, proposal, sender=sender)
    #    try:
    #        _log_org_email(msg, proposal.applicant, proposal.submitter, sender=sender)
    #    except:
    #        _log_org_email(msg, proposal.submitter, proposal.submitter, sender=sender)
    if proposal.org_applicant:
        _log_org_email(msg, proposal.org_applicant, proposal.submitter, sender=sender)
    else:
        _log_user_email(msg, proposal.submitter, proposal.submitter, sender=sender)


def send_application_fee_confirmation_tclass_email_notification(
    request, application_fee, invoice, recipients, is_test=False
):
    email = ApplicationFeeConfirmationTClassSendNotificationEmail()
    # url = request.build_absolute_uri(reverse('external-proposal-detail',kwargs={'proposal_pk': proposal.id}))

    proposal = application_fee.proposal
    context = {
        "lodgement_number": proposal.lodgement_number,
        # 'url': url,
    }

    filename = "confirmation.pdf"
    doc = create_confirmation_pdf_bytes(filename, invoice, application_fee)
    # doc = create_invoice_pdf_bytes(filename, invoice, proposal)
    attachment = (filename, doc, "application/pdf")

    msg = email.send(recipients, attachments=[attachment], context=context)
    if is_test:
        return

    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_proposal_email(msg, proposal, sender=sender)
    if proposal.org_applicant:
        _log_org_email(msg, proposal.org_applicant, proposal.submitter, sender=sender)
    else:
        _log_user_email(msg, proposal.submitter, proposal.submitter, sender=sender)


def send_invoice_tclass_email_notification(
    sender, booking, invoice, recipients, is_test=False
):
    email = InvoiceTClassSendNotificationEmail()

    context = {
        "booking_number": booking.booking_number,
        # 'url': url,
    }

    filename = "invoice.pdf"
    doc = create_invoice_pdf_bytes(filename, invoice, booking.proposal)
    attachment = (filename, doc, "application/pdf")

    msg = email.send(recipients, attachments=[attachment], context=context)
    if is_test:
        return

    _log_proposal_email(msg, booking.proposal, sender=sender)
    # _log_org_email(msg, booking.proposal.applicant, booking.proposal.submitter, sender=sender)
    if booking.proposal.org_applicant:
        _log_org_email(
            msg,
            booking.proposal.org_applicant,
            booking.proposal.submitter,
            sender=sender,
        )
    else:
        _log_user_email(
            msg, booking.proposal.submitter, booking.proposal.submitter, sender=sender
        )


def send_confirmation_tclass_email_notification(
    sender, booking, invoice, recipients, is_test=False
):
    email = ConfirmationTClassSendNotificationEmail()

    context = {
        "booking_number": booking.booking_number,
    }

    filename = "confirmation.pdf"
    doc = create_confirmation_pdf_bytes(filename, invoice, booking)
    attachment = (filename, doc, "application/pdf")

    msg = email.send(recipients, attachments=[attachment], context=context)
    if is_test:
        return

    _log_proposal_email(msg, booking.proposal, sender=sender)
    # _log_org_email(msg, booking.proposal.applicant, booking.proposal.submitter, sender=sender)
    if booking.proposal.org_applicant:
        _log_org_email(
            msg,
            booking.proposal.org_applicant,
            booking.proposal.submitter,
            sender=sender,
        )
    else:
        _log_user_email(
            msg, booking.proposal.submitter, booking.proposal.submitter, sender=sender
        )


def send_monthly_confirmation_tclass_email_notification(
    sender, booking, recipients, is_test=False
):
    """Monthly confirmation has deferred invoicing, deferred to the following month.
    So invoice is created later by Cron"""
    email = ConfirmationTClassSendNotificationEmail()
    # url = request.build_absolute_uri(reverse('external-proposal-detail',kwargs={'proposal_pk': proposal.id}))

    context = {
        "booking_number": booking.booking_number,
    }

    filename = "monthly_confirmation.pdf"
    doc = create_monthly_confirmation_pdf_bytes(filename, booking)
    attachment = (filename, doc, "application/pdf")

    msg = email.send(recipients, attachments=[attachment], context=context)
    if is_test:
        return

    _log_proposal_email(msg, booking.proposal, sender=sender)
    # _log_org_email(msg, booking.proposal.applicant, booking.proposal.submitter, sender=sender)
    if booking.proposal.org_applicant:
        _log_org_email(
            msg,
            booking.proposal.org_applicant,
            booking.proposal.submitter,
            sender=sender,
        )
    else:
        _log_user_email(
            msg, booking.proposal.submitter, booking.proposal.submitter, sender=sender
        )


def send_monthly_invoice_tclass_email_notification(
    sender, booking, invoice, recipients, is_test=False
):
    email = MonthlyInvoiceTClassSendNotificationEmail()

    context = {
        "booking_number": booking.booking_number,
    }

    filename = "monthly_invoice.pdf"
    doc = create_invoice_pdf_bytes(filename, invoice, booking.proposal)
    attachment = (filename, doc, "application/pdf")

    msg = email.send(recipients, attachments=[attachment], context=context)
    if is_test:
        return

    _log_proposal_email(msg, booking.proposal, sender=sender)
    if booking.proposal.org_applicant:
        _log_org_email(
            msg,
            booking.proposal.org_applicant,
            booking.proposal.submitter,
            sender=sender,
        )
    else:
        _log_user_email(
            msg, booking.proposal.submitter, booking.proposal.submitter, sender=sender
        )


def send_monthly_invoices_failed_tclass(booking_ids):
    """Internal failed notification email for Monthly Invoicing script"""
    email = MonthlyInvoicesFailedTClassEmail()

    context = {
        "bookings": Booking.objects.filter(id__in=booking_ids).values_list(
            "id",
            "admission_number",
            "proposal__lodgement_number",
            "proposal__org_applicant__organisation__name",
        ),
    }
    email.send(settings.NOTIFICATION_EMAIL, context=context)


def send_payment_due_notification_failed_tclass(bookings):
    """Internal failed notification email for Payment Due Notification script"""
    email = PaymentDueNotificationFailedTClassEmail()

    context = {"bookings": bookings}
    email.send(settings.NOTIFICATION_EMAIL, context=context)


def send_invoice_payment_due_tclass_email_notification(
    sender, bookings, recipients, is_test=False
):
    email = SendPaymentDueNotificationTClassEmail()

    context = {
        "bookings": bookings,
    }

    email.send(bookings[0].proposal.submitter.email, context=context)
    # sender = sender if sender else settings.DEFAULT_FROM_EMAIL
    # _log_proposal_email(msg, booking.proposal, sender=sender)
    # if booking.proposal.org_applicant:
    #    _log_org_email(msg, booking.proposal.org_applicant, booking.proposal.submitter, sender=sender)
    # else:
    #    _log_user_email(msg, booking.proposal.submitter, booking.proposal.submitter, sender=sender)


def send_invoice_payment_due_tclass_external_email_notification(
    sender, booking, recipients, is_test=False
):
    email = SendExternalPaymentDueNotificationTClassEmail()

    context = {
        "booking": booking,
    }

    msg = email.send(booking.proposal.submitter.email, context=context)
    sender = sender if sender else settings.DEFAULT_FROM_EMAIL
    _log_proposal_email(msg, booking.proposal, sender=sender)
    if booking.proposal.org_applicant:
        _log_org_email(
            msg,
            booking.proposal.org_applicant,
            booking.proposal.submitter,
            sender=sender,
        )
    else:
        _log_user_email(
            msg, booking.proposal.submitter, booking.proposal.submitter, sender=sender
        )


def _log_proposal_email(email_message, proposal, sender=None):
    from leaseslicensing.components.proposals.models import ProposalLogEntry

    if isinstance(
        email_message,
        (
            EmailMultiAlternatives,
            EmailMessage,
        ),
    ):
        # TODO this will log the plain text body, should we log the html instead
        text = email_message.body
        subject = email_message.subject
        fromm = smart_text(sender) if sender else smart_text(email_message.from_email)
        # the to email is normally a list
        if isinstance(email_message.to, list):
            to = ",".join(email_message.to)
        else:
            to = smart_text(email_message.to)
        # we log the cc and bcc in the same cc field of the log entry as a ',' comma separated string
        all_ccs = []
        if email_message.cc:
            all_ccs += list(email_message.cc)
        if email_message.bcc:
            all_ccs += list(email_message.bcc)
        all_ccs = ",".join(all_ccs)

    else:
        text = smart_text(email_message)
        subject = ""
        to = proposal.submitter.email
        fromm = smart_text(sender) if sender else SYSTEM_NAME
        all_ccs = ""

    customer = proposal.submitter

    staff = sender

    kwargs = {
        "subject": subject,
        "text": text,
        "proposal": proposal,
        "customer": customer,
        "staff": staff,
        "to": to,
        "fromm": fromm,
        "cc": all_ccs,
    }

    email_entry = ProposalLogEntry.objects.create(**kwargs)

    return email_entry


def _log_org_email(email_message, organisation, customer, sender=None):
    from leaseslicensing.components.organisations.models import OrganisationLogEntry

    if isinstance(
        email_message,
        (
            EmailMultiAlternatives,
            EmailMessage,
        ),
    ):
        # TODO this will log the plain text body, should we log the html instead
        text = email_message.body
        subject = email_message.subject
        fromm = smart_text(sender) if sender else smart_text(email_message.from_email)
        # the to email is normally a list
        if isinstance(email_message.to, list):
            to = ",".join(email_message.to)
        else:
            to = smart_text(email_message.to)
        # we log the cc and bcc in the same cc field of the log entry as a ',' comma separated string
        all_ccs = []
        if email_message.cc:
            all_ccs += list(email_message.cc)
        if email_message.bcc:
            all_ccs += list(email_message.bcc)
        all_ccs = ",".join(all_ccs)

    else:
        text = smart_text(email_message)
        subject = ""
        to = customer
        fromm = smart_text(sender) if sender else SYSTEM_NAME
        all_ccs = ""

    customer = customer

    staff = sender

    kwargs = {
        "subject": subject,
        "text": text,
        "organisation": organisation,
        "customer": customer,
        "staff": staff,
        "to": to,
        "fromm": fromm,
        "cc": all_ccs,
    }

    email_entry = OrganisationLogEntry.objects.create(**kwargs)

    return email_entry


def _log_user_email(email_message, emailuser, customer, sender=None):
    from ledger.accounts.models import EmailUserLogEntry

    if isinstance(
        email_message,
        (
            EmailMultiAlternatives,
            EmailMessage,
        ),
    ):
        # TODO this will log the plain text body, should we log the html instead
        text = email_message.body
        subject = email_message.subject
        fromm = smart_text(sender) if sender else smart_text(email_message.from_email)
        # the to email is normally a list
        if isinstance(email_message.to, list):
            to = ",".join(email_message.to)
        else:
            to = smart_text(email_message.to)
        # we log the cc and bcc in the same cc field of the log entry as a ',' comma separated string
        all_ccs = []
        if email_message.cc:
            all_ccs += list(email_message.cc)
        if email_message.bcc:
            all_ccs += list(email_message.bcc)
        all_ccs = ",".join(all_ccs)

    else:
        text = smart_text(email_message)
        subject = ""
        to = customer
        fromm = smart_text(sender) if sender else SYSTEM_NAME
        all_ccs = ""

    customer = customer

    staff = sender

    kwargs = {
        "subject": subject,
        "text": text,
        "emailuser": emailuser,
        "customer": customer,
        "staff": staff,
        "to": to,
        "fromm": fromm,
        "cc": all_ccs,
    }

    email_entry = EmailUserLogEntry.objects.create(**kwargs)

    return email_entry
