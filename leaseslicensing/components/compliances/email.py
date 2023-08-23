import logging

from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.urls import reverse
from django.utils.encoding import smart_text

from leaseslicensing.components.emails.emails import TemplateEmailBase
from leaseslicensing.ledger_api_utils import (
    retrieve_default_from_email_user,
    retrieve_email_user,
)

logger = logging.getLogger(__name__)

SYSTEM_NAME = settings.SYSTEM_NAME_SHORT + " Automated Message"


class ComplianceExternalSubmitSendNotificationEmail(TemplateEmailBase):
    def __init__(self):
        super().__init__()
        self.subject = "{} - Lease or Licence compliance requirement submitted successfully.".format(
            settings.DEP_NAME
        )
        self.html_template = (
            "leaseslicensing/emails/compliances/send_external_submit_notification.html"
        )
        self.txt_template = (
            "leaseslicensing/emails/compliances/send_external_submit_notification.txt"
        )


class ComplianceSubmitSendNotificationEmail(TemplateEmailBase):
    def __init__(self):
        super().__init__()
        self.subject = "{} - A new Compliance has been submitted.".format(
            settings.DEP_NAME
        )
        self.html_template = (
            "leaseslicensing/emails/compliances/send_submit_notification.html"
        )
        self.txt_template = (
            "leaseslicensing/emails/compliances/send_submit_notification.txt"
        )


class ComplianceAcceptNotificationEmail(TemplateEmailBase):
    def __init__(self):
        super().__init__()
        self.subject = "{} - Lease or Licence compliance requirement approved.".format(
            settings.DEP_NAME
        )
        self.html_template = (
            "leaseslicensing/emails/compliances/compliance_accept_notification.html"
        )
        self.txt_template = (
            "leaseslicensing/emails/compliances/compliance_accept_notification.txt"
        )


class ComplianceAmendmentRequestSendNotificationEmail(TemplateEmailBase):
    def __init__(self):
        super().__init__()
        self.subject = (
            "{} - Lease or Licence compliance requirement requires amendments.".format(
                settings.DEP_NAME
            )
        )
        self.html_template = (
            "leaseslicensing/emails/compliances/send_amendment_notification.html"
        )
        self.txt_template = (
            "leaseslicensing/emails/compliances/send_amendment_notification.txt"
        )


class ComplianceReminderNotificationEmail(TemplateEmailBase):
    def __init__(self, customer_status_display):
        super().__init__()
        self.subject = "{} - Leases or Licence compliance requirement {}.".format(
            settings.DEP_NAME, customer_status_display.lower()
        )
        self.html_template = (
            "leaseslicensing/emails/compliances/send_reminder_notification.html"
        )
        self.txt_template = (
            "leaseslicensing/emails/compliances/send_reminder_notification.txt"
        )


class ComplianceInternalReminderNotificationEmail(TemplateEmailBase):
    def __init__(self):
        super().__init__()
        self.subject = (
            "{} - A Compliance with requirements has passed the due date.".format(
                settings.DEP_NAME
            )
        )
        self.html_template = "leaseslicensing/emails/compliances/send_internal_reminder_notification.html"
        self.txt_template = (
            "leaseslicensing/emails/compliances/send_internal_reminder_notification.txt"
        )


class ComplianceDueNotificationEmail(TemplateEmailBase):
    def __init__(self):
        super().__init__()
        self.subject = "{} - Lease or Licence compliance requirement due.".format(
            settings.DEP_NAME
        )
        self.html_template = (
            "leaseslicensing/emails/compliances/send_due_notification.html"
        )
        self.txt_template = (
            "leaseslicensing/emails/compliances/send_due_notification.txt"
        )


class ComplianceInternalDueNotificationEmail(TemplateEmailBase):
    def __init__(self):
        super().__init__()
        self.subject = "{} - Lease or Licence compliance requirement is due for submission.".format(
            settings.DEP_NAME
        )
        self.html_template = (
            "leaseslicensing/emails/compliances/send_internal_due_notification.html"
        )
        self.txt_template = (
            "leaseslicensing/emails/compliances/send_internal_due_notification.txt"
        )


class ComplianceNotificationOnlyEmail(TemplateEmailBase):
    def __init__(self):
        super().__init__()
        self.subject = "{} - Lease or Licence requirement notification.".format(
            settings.DEP_NAME
        )
        self.html_template = (
            "leaseslicensing/emails/compliances/send_notification_only_email.html"
        )
        self.txt_template = (
            "leaseslicensing/emails/compliances/send_notification_only_email.txt"
        )


class ComplianceInternalNotificationOnlyEmail(TemplateEmailBase):
    def __init__(self):
        super().__init__()
        self.subject = "A Compliance with requirements is due for submission."
        self.html_template = "leaseslicensing/emails/compliances/send_internal_notification_only_email.html"
        self.txt_template = "leaseslicensing/emails/compliances/send_internal_notification_only_email.txt"


def send_amendment_email_notification(
    amendment_request, request, compliance, is_test=False
):
    email = ComplianceAmendmentRequestSendNotificationEmail()
    # reason = amendment_request.get_reason_display()
    reason = amendment_request.reason.reason
    url = request.build_absolute_uri(
        reverse("external-compliance-detail", kwargs={"compliance_pk": compliance.id})
    )
    url = "".join(url.split("-internal"))
    login_url = request.build_absolute_uri(reverse("external"))
    login_url = "".join(login_url.split("-internal"))
    context = {
        "compliance": compliance,
        "reason": reason,
        "amendment_request_text": amendment_request.text,
        "url": url,
    }

    submitter_email = compliance.submitter_email

    all_ccs = []
    if compliance.proposal.org_applicant and compliance.proposal.org_applicant.email:
        cc_list = compliance.proposal.org_applicant.email
        if cc_list:
            all_ccs = [cc_list]
    msg = email.send(submitter_email, cc=all_ccs, context=context)
    if is_test:
        return

    sender = request.user if request else retrieve_default_from_email_user()

    _log_compliance_email(msg, compliance, sender=sender)


def send_referral_email_notification(referral, recipients, request, reminder=False):
    compliance = referral.compliance
    proposal = compliance.proposal
    email = TemplateEmailBase(
        subject=f"Referral Request for Compliance: {compliance.lodgement_number}",
        html_template="leaseslicensing/emails/compliances/send_referral_notification.html",
        txt_template="leaseslicensing/emails/compliances/send_referral_notification.txt",
    )
    url = request.build_absolute_uri(
        reverse(
            "internal-compliance-detail",
            kwargs={"pk": compliance.id},
        )
    )

    context = {
        "proposal": proposal,
        "compliance": compliance,
        "url": url,
        "reminder": reminder,
        "comments": referral.text,
        "proposed_start_date": "",
    }

    msg = email.send(recipients, context=context)

    sender = request.user if request else retrieve_default_from_email_user()

    _log_compliance_email(msg, compliance, sender=sender)

    if proposal.org_applicant:
        _log_org_email(msg, proposal.org_applicant, referral.referral, sender=sender)
    elif proposal.ind_applicant:
        _log_user_email(msg, proposal.ind_applicant, referral.referral, sender=sender)


def send_referral_complete_email_notification(referral, request):
    sent_by = retrieve_email_user(referral.sent_by)
    compliance = referral.compliance
    proposal = compliance.proposal
    application_type = proposal.application_type.name_display
    email_user = retrieve_email_user(referral.referral)

    email = TemplateEmailBase(
        subject=(
            f"{email_user.get_full_name()} has Completed Referral for {application_type} "
            f"Compliance {compliance.lodgement_number}"
        ),
        html_template="leaseslicensing/emails/compliances/send_referral_complete_notification.html",
        txt_template="leaseslicensing/emails/compliances/send_referral_complete_notification.txt",
    )

    email.subject = sent_by.email + ": " + email.subject
    url = request.build_absolute_uri(
        reverse("internal-proposal-detail", kwargs={"pk": proposal.id})
    )

    context = {
        "completed_by": email_user.get_full_name(),
        "application_type": application_type,
        "compliance": compliance,
        "proposal": compliance.proposal,
        "url": url,
        "referral_comments": referral.referral_text,
    }

    msg = email.send(sent_by.email, context=context)
    sender = request.user if request else retrieve_default_from_email_user()

    _log_compliance_email(msg, compliance, sender=sender)

    if proposal.org_applicant:
        _log_org_email(
            msg,
            proposal.org_applicant,
            referral.referral,
            sender=sender,
        )
    elif proposal.ind_applicant:
        _log_user_email(
            msg,
            proposal.ind_applicant,
            referral.referral,
            sender=sender,
        )


def send_pending_referrals_complete_email_notification(referral, request):
    compliance = referral.compliance
    proposal = compliance.proposal
    application_type = proposal.application_type.name_display
    email = TemplateEmailBase(
        subject=(
            f"All Pending Referrals for {application_type} "
            f"Compliance: {compliance.lodgement_number} have been completed."
        ),
        html_template="leaseslicensing/emails/compliances/send_pending_referrals_complete_notification.html",
        txt_template="leaseslicensing/emails/compliances/send_pending_referrals_complete_notification.txt",
    )

    url = request.build_absolute_uri(
        reverse("internal-compliance-detail", kwargs={"pk": compliance.id})
    )

    context = {
        "referral": referral,
        "compliance": referral.compliance,
        "url": url,
    }
    recipients = proposal.assessor_recipients
    msg = email.send(recipients, context=context)

    sender = request.user if request else retrieve_default_from_email_user()

    _log_compliance_email(msg, compliance, sender=sender)


def send_reminder_email_notification(compliance, is_test=False):
    """Used by the management command, therefore have no request object - therefore explicitly defining base_url"""
    email = ComplianceReminderNotificationEmail(
        compliance.get_customer_status_display()
    )
    url = settings.SITE_URL if settings.SITE_URL else ""
    url += reverse(
        "external-compliance-detail", kwargs={"compliance_pk": compliance.id}
    )
    login_url = settings.SITE_URL if settings.SITE_URL else ""
    login_url += reverse("external")

    context = {"compliance": compliance, "url": url, "login_url": login_url}

    submitter = compliance.submitter_emailuser

    all_ccs = []
    if compliance.proposal.org_applicant and compliance.proposal.org_applicant.email:
        cc_list = compliance.proposal.org_applicant.email
        if cc_list:
            all_ccs = [cc_list]
    msg = email.send(submitter.email, cc=all_ccs, context=context)
    if is_test:
        return

    sender = retrieve_default_from_email_user()

    _log_compliance_email(msg, compliance, sender=sender)

    if compliance.proposal.org_applicant:
        _log_org_email(
            msg,
            compliance.proposal.org_applicant,
            submitter,
            sender=sender,
        )
    else:
        _log_user_email(msg, compliance.proposal.submitter, submitter, sender=sender)


def send_internal_reminder_email_notification(compliance, is_test=False):
    email = ComplianceInternalReminderNotificationEmail()
    # url = request.build_absolute_uri(reverse('external-compliance-detail',kwargs={'compliance_pk': compliance.id}))
    url = settings.SITE_URL
    url += reverse("internal-compliance-detail", kwargs={"pk": compliance.id})
    if "-internal" not in url:
        # add it. This email is for internal staff
        url = f"-internal.{settings.SITE_DOMAIN}".join(
            url.split("." + settings.SITE_DOMAIN)
        )

    context = {"compliance": compliance, "url": url}

    msg = email.send(compliance.proposal.assessor_recipients, context=context)
    if is_test:
        return

    sender = retrieve_default_from_email_user()

    _log_compliance_email(msg, compliance, sender=sender)


def send_due_email_notification(compliance, is_test=False):
    email = ComplianceDueNotificationEmail()
    url = settings.SITE_URL
    url += reverse(
        "external-compliance-detail", kwargs={"compliance_pk": compliance.id}
    )
    context = {"compliance": compliance, "url": url}

    submitter = compliance.submitter_emailuser

    all_ccs = []

    if compliance.proposal.org_applicant and compliance.proposal.org_applicant.email:
        cc_list = compliance.proposal.org_applicant.email
        if cc_list:
            all_ccs = [cc_list]

    msg = email.send(submitter.email, cc=all_ccs, context=context)
    if is_test:
        return

    sender = retrieve_default_from_email_user()

    _log_compliance_email(msg, compliance, sender=sender)

    if compliance.proposal.org_applicant:
        _log_org_email(
            msg,
            compliance.proposal.org_applicant,
            submitter,
            sender=sender.id,
        )
    else:
        _log_user_email(
            msg,
            compliance.proposal.submitter,
            submitter,
            sender=sender.id,
        )


def send_internal_due_email_notification(compliance, is_test=False):
    email = ComplianceInternalDueNotificationEmail()
    url = settings.SITE_URL
    url += reverse("internal-compliance-detail", kwargs={"pk": compliance.id})
    if "-internal" not in url:
        # add it. This email is for internal staff
        url = f"-internal.{settings.SITE_DOMAIN}".join(
            url.split("." + settings.SITE_DOMAIN)
        )

    context = {"compliance": compliance, "url": url}

    msg = email.send(compliance.proposal.assessor_recipients, context=context)
    if is_test:
        return

    sender = retrieve_default_from_email_user()

    _log_compliance_email(msg, compliance, sender=sender)


def send_compliance_accept_email_notification(compliance, request, is_test=False):
    email = ComplianceAcceptNotificationEmail()

    context = {"compliance": compliance}
    submitter_email = compliance.submitter_email

    all_ccs = []
    if compliance.proposal.org_applicant and compliance.proposal.org_applicant.email:
        cc_list = compliance.proposal.org_applicant.email
        if cc_list:
            all_ccs = [cc_list]

    msg = email.send(submitter_email, cc=all_ccs, context=context)
    if is_test:
        return

    sender = request.user if request else retrieve_default_from_email_user()
    _log_compliance_email(msg, compliance, sender=sender)

    if compliance.proposal.org_applicant:
        _log_org_email(
            msg, compliance.proposal.org_applicant, compliance.submitter, sender=sender
        )
    else:
        _log_user_email(
            msg, compliance.proposal.submitter, compliance.submitter, sender=sender
        )


def send_external_submit_email_notification(request, compliance, is_test=False):
    email = ComplianceExternalSubmitSendNotificationEmail()
    url = request.build_absolute_uri(
        reverse("external-compliance-detail", kwargs={"compliance_pk": compliance.id})
    )
    url = "".join(url.split("-internal"))

    submitter_id = (
        compliance.submitter if compliance.submitter else compliance.proposal.submitter
    )
    submitter = retrieve_email_user(submitter_id)
    context = {
        "compliance": compliance,
        "submitter": submitter.get_full_name(),
        "url": url,
    }

    all_ccs = []
    organisation = compliance.proposal.org_applicant
    if organisation and organisation.ledger_organisation_email:
        all_ccs = [organisation.ledger_organisation_email]

    msg = email.send(submitter.email, cc=all_ccs, context=context)
    if is_test:
        return

    sender = request.user if request else retrieve_default_from_email_user()

    _log_compliance_email(msg, compliance, sender=sender)

    if compliance.proposal.org_applicant:
        _log_org_email(
            msg, compliance.proposal.org_applicant, compliance.submitter, sender=sender
        )
    else:
        _log_user_email(
            msg, compliance.proposal.submitter, compliance.submitter, sender=sender
        )


def send_submit_email_notification(request, compliance, is_test=False):
    email = ComplianceSubmitSendNotificationEmail()
    url = request.build_absolute_uri(
        reverse("internal-compliance-detail", kwargs={"pk": compliance.id})
    )
    if "-internal" not in url:
        # add it. This email is for internal staff
        url = f"-internal.{settings.SITE_DOMAIN}".join(
            url.split("." + settings.SITE_DOMAIN)
        )

    context = {"compliance": compliance, "url": url}

    msg = email.send(compliance.proposal.assessor_recipients, context=context)
    if is_test:
        return

    sender = request.user if request else retrieve_default_from_email_user()
    _log_compliance_email(msg, compliance, sender=sender)

    if compliance.proposal.org_applicant:
        _log_org_email(
            msg, compliance.proposal.org_applicant, compliance.submitter, sender=sender
        )
    else:
        _log_user_email(
            msg, compliance.proposal.submitter, compliance.submitter, sender=sender
        )


def send_notification_only_email(compliance, is_test=False):
    # email = ComplianceDueNotificationEmail()
    email = ComplianceNotificationOnlyEmail()
    # url = request.build_absolute_uri(reverse('external-compliance-detail',kwargs={'compliance_pk': compliance.id}))
    url = settings.SITE_URL
    url += reverse(
        "external-compliance-detail", kwargs={"compliance_pk": compliance.id}
    )
    context = {"compliance": compliance, "url": url}

    submitter_email = compliance.submitter_email

    all_ccs = []
    if compliance.proposal.org_applicant and compliance.proposal.org_applicant.email:
        cc_list = compliance.proposal.org_applicant.email
        if cc_list:
            all_ccs = [cc_list]

    msg = email.send(submitter_email, cc=all_ccs, context=context)
    if is_test:
        return

    sender = retrieve_default_from_email_user()

    _log_compliance_email(msg, compliance, sender=sender)

    if compliance.proposal.org_applicant:
        _log_org_email(
            msg,
            compliance.proposal.org_applicant,
            compliance.submitter,
            sender=sender,
        )
    else:
        _log_user_email(
            msg, compliance.proposal.submitter, compliance.submitter, sender=sender
        )


def send_internal_notification_only_email(compliance, is_test=False):
    email = ComplianceInternalNotificationOnlyEmail()
    url = settings.SITE_URL
    url += reverse("internal-compliance-detail", kwargs={"pk": compliance.id})
    if "-internal" not in url:
        # add it. This email is for internal staff
        url = f"-internal.{settings.SITE_DOMAIN}".join(
            url.split("." + settings.SITE_DOMAIN)
        )

    context = {"compliance": compliance, "url": url}

    msg = email.send(compliance.proposal.assessor_recipients, context=context)
    if is_test:
        return

    sender = retrieve_default_from_email_user()
    _log_compliance_email(msg, compliance, sender=sender)

    if compliance.proposal.org_applicant:
        _log_org_email(
            msg,
            compliance.proposal.org_applicant,
            compliance.submitter,
            sender=sender,
        )
    else:
        _log_user_email(
            msg, compliance.proposal.submitter, compliance.submitter, sender=sender
        )


def _log_compliance_email(email_message, compliance, sender=None):
    from leaseslicensing.components.compliances.models import ComplianceLogEntry

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
        to = compliance.submitter_email
        fromm = smart_text(sender) if sender else SYSTEM_NAME
        all_ccs = ""

    customer = compliance.submitter

    staff = sender

    if type(staff) is not int:
        if not hasattr(staff, "id"):
            raise ValueError("staff must be an int (i.e. EmailUser.id)")
        staff = staff.id

    kwargs = {
        "subject": subject,
        "text": text,
        "compliance": compliance,
        "customer": customer,
        "staff": staff,
        "to": to,
        "fromm": fromm,
        "cc": all_ccs,
    }

    email_entry = ComplianceLogEntry.objects.create(**kwargs)

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
        to = customer.email
        fromm = smart_text(sender) if sender else SYSTEM_NAME
        all_ccs = ""

    staff = sender

    if type(staff) is not int:
        if not hasattr(staff, "id"):
            raise ValueError("staff must be an int (i.e. EmailUser.id)")
        staff = staff.id

    kwargs = {
        "subject": subject,
        "text": text,
        "organisation": organisation,
        "customer": customer.id,
        "staff": staff,
        "to": to,
        "fromm": fromm,
        "cc": all_ccs,
    }

    email_entry = OrganisationLogEntry.objects.create(**kwargs)

    return email_entry


def _log_user_email(email_message, emailuser, customer, sender=None):
    from leaseslicensing.components.users.models import EmailUserLogEntry

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
        to = customer.email
        fromm = smart_text(sender) if sender else SYSTEM_NAME
        all_ccs = ""

    staff = sender

    if type(staff) is not int:
        if not hasattr(staff, "id"):
            raise ValueError("staff must be an int (i.e. EmailUser.id)")
        staff = staff.id

    if type(customer) is not int:
        if not hasattr(customer, "id"):
            raise ValueError("customer must be an int (i.e. EmailUser.id)")
        customer = customer.id

    kwargs = {
        "subject": subject,
        "text": text,
        "email_user": emailuser,
        "customer": customer,
        "staff": staff,
        "to": to,
        "fromm": fromm,
        "cc": all_ccs,
    }

    email_entry = EmailUserLogEntry.objects.create(**kwargs)

    return email_entry
