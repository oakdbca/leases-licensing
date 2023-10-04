import datetime
import logging
import re

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import JSONField, Q
from django.db.models.deletion import ProtectedError
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils import timezone
from ledger_api_client.ledger_models import EmailUserRO as EmailUser

from leaseslicensing.components.approvals.email import (
    send_approval_cancel_email_notification,
    send_approval_expire_email_notification,
    send_approval_reinstate_email_notification,
    send_approval_renewal_email_notification,
    send_approval_surrender_email_notification,
    send_approval_suspend_email_notification,
)
from leaseslicensing.components.compliances.models import Compliance
from leaseslicensing.components.invoicing.models import Invoice
from leaseslicensing.components.main.models import (
    CommunicationsLogEntry,
    Document,
    LicensingModelVersioned,
    RevisionedMixin,
    SecureFileField,
    UserAction,
)
from leaseslicensing.components.main.related_item import RelatedItem
from leaseslicensing.components.organisations.models import Organisation
from leaseslicensing.components.organisations.utils import get_organisation_ids_for_user
from leaseslicensing.components.proposals.models import (
    Proposal,
    ProposalType,
    ProposalUserAction,
    RequirementDocument,
)
from leaseslicensing.helpers import is_customer, user_ids_in_group
from leaseslicensing.ledger_api_utils import retrieve_email_user
from leaseslicensing.settings import PROPOSAL_TYPE_AMENDMENT, PROPOSAL_TYPE_RENEWAL

logger = logging.getLogger(__name__)


def update_approval_doc_filename(instance, filename):
    return f"approval_documents/{instance.id}/{filename}"


def update_approval_comms_log_filename(instance, filename):
    return "proposals/{}/approvals/{}/communications/{}".format(
        instance.log_entry.approval.current_proposal.id,
        instance.log_entry.approval.id,
        filename,
    )


def update_approval_cancellation_doc_filename(instance, filename):
    return "/approval_cancellation_documents/{}/{}".format(
        instance.id,
        filename,
    )


def update_approval_surrender_doc_filename(instance, filename):
    return "approval_surrender_documents/{}/{}".format(
        instance.id,
        filename,
    )


def update_approval_suspension_doc_filename(instance, filename):
    return "approval_suspension_documents/{}/{}".format(
        instance.id,
        filename,
    )


class ApprovalDocument(Document, RevisionedMixin):
    REASON_NEW = "new"
    REASON_AMENDED = "amended"
    REASON_RENEWED = "renewed"
    REASON_REISSUED = "reissued"
    REASON_INVOICING_UPDATED = "invoicing_updated"
    REASON_CHOICES = (
        (REASON_NEW, "New"),
        (REASON_AMENDED, "Amended"),
        (REASON_RENEWED, "Renewed"),
        (REASON_REISSUED, "Reissued"),
        (REASON_INVOICING_UPDATED, "Invoicing updated"),
    )

    approval = models.ForeignKey(
        "Approval", related_name="documents", on_delete=models.CASCADE
    )
    _file = SecureFileField(upload_to=update_approval_doc_filename, max_length=512)
    can_delete = models.BooleanField(
        default=True
    )  # after initial submit prevent document from being deleted
    reason = models.CharField(max_length=25, choices=REASON_CHOICES, default="new")

    def delete(self):
        if self.can_delete:
            return super().delete()
        logger.info(
            "Cannot delete existing document object after Application has been submitted "
            f"(including document submitted before Application pushback to status Draft): {self.name}"
        )

    def user_has_object_permission(self, user_id):
        """Used by the secure documents api to determine if the user can view the instance and any attached documents"""
        return self.approval.user_has_object_permission(user_id)

    @property
    def approval_lodgement_sequence(self):
        return self.approval.lodgement_sequence


class Meta:
    app_label = "leaseslicensing"


class ApprovalType(RevisionedMixin):
    APPROVAL_TYPE_LEASE = "lease"
    APPROVAL_TYPE_LICENCE = "licence"
    APPROVAL_TYPE_CHOICES = (
        (APPROVAL_TYPE_LEASE, "Lease"),
        (APPROVAL_TYPE_LICENCE, "Licence"),
    )
    type = models.CharField(max_length=10, choices=APPROVAL_TYPE_CHOICES, null=True)
    name = models.CharField(max_length=200, unique=True)
    details_placeholder = models.CharField(max_length=200, blank=True)
    gst_free = models.BooleanField(default=False)
    approvaltypedocumenttypes = models.ManyToManyField(
        "ApprovalTypeDocumentType", through="ApprovalTypeDocumentTypeOnApprovalType"
    )

    class Meta:
        app_label = "leaseslicensing"

    def __str__(self):
        return self.name


class ApprovalTypeDocumentType(RevisionedMixin):
    name = models.CharField(max_length=200, unique=True)
    # Whether this document type is the license document
    is_license_document = models.BooleanField(default=False)
    # Whether this document type is the cover letter
    is_cover_letter = models.BooleanField(default=False)
    # Whether this document type is the sign off sheet
    is_sign_off_sheet = models.BooleanField(default=False)

    class Meta:
        app_label = "leaseslicensing"
        # A document must be either-or or none
        constraints = [
            models.CheckConstraint(
                check=Q(
                    ~Q(is_license_document=True, is_cover_letter=True),
                    ~Q(is_license_document=True, is_sign_off_sheet=True),
                    ~Q(is_cover_letter=True, is_sign_off_sheet=True),
                    _connector="AND",
                ),
                name="only_one_or_none_of_license_document_cover_letter_sign_off_sheet",
            )
        ]

    def __str__(self):
        return self.name


class ApprovalTypeDocumentTypeOnApprovalType(RevisionedMixin):
    approval_type = models.ForeignKey(ApprovalType, on_delete=models.CASCADE)
    approval_type_document_type = models.ForeignKey(
        ApprovalTypeDocumentType, on_delete=models.CASCADE
    )
    mandatory = models.BooleanField(default=False)

    class Meta:
        app_label = "leaseslicensing"
        unique_together = ("approval_type", "approval_type_document_type")


class Approval(LicensingModelVersioned):
    MODEL_PREFIX = "L"

    APPROVAL_STATUS_CURRENT = "current"
    APPROVAL_STATUS_CURRENT_PENDING_RENEWAL_REVIEW = "current_pending_renewal_review"
    APPROVAL_STATUS_CURRENT_PENDING_RENEWAL = "current_pending_renewal"
    APPROVAL_STATUS_EXPIRED = "expired"
    APPROVAL_STATUS_CANCELLED = "cancelled"
    APPROVAL_STATUS_SURRENDERED = "surrendered"
    APPROVAL_STATUS_SUSPENDED = "suspended"
    APPROVAL_STATUS_EXTENDED = "extended"
    APPROVAL_STATUS_AWAITING_PAYMENT = "awaiting_payment"
    APPROVAL_STATUS_CURRENT_EDITING_INVOICING = "current_editing_invoicing"

    STATUS_CHOICES = (
        (APPROVAL_STATUS_CURRENT, "Current"),
        (
            APPROVAL_STATUS_CURRENT_PENDING_RENEWAL_REVIEW,
            "Current (Pending Renewal Review)",
        ),
        (APPROVAL_STATUS_CURRENT_PENDING_RENEWAL, "Current (Pending Renewal)"),
        (APPROVAL_STATUS_EXPIRED, "Expired"),
        (APPROVAL_STATUS_CANCELLED, "Cancelled"),
        (APPROVAL_STATUS_SURRENDERED, "Surrendered"),
        (APPROVAL_STATUS_SUSPENDED, "Suspended"),
        (APPROVAL_STATUS_EXTENDED, "Extended"),
        (APPROVAL_STATUS_AWAITING_PAYMENT, "Awaiting Payment"),
        (APPROVAL_STATUS_CURRENT_EDITING_INVOICING, "Current (Editing Invoicing)"),
    )
    approval_type = models.ForeignKey(ApprovalType, on_delete=models.PROTECT, null=True)
    status = models.CharField(
        max_length=40, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0]
    )
    licence_document = models.ForeignKey(
        ApprovalDocument,
        blank=True,
        null=True,
        related_name="licence_document",
        on_delete=models.SET_NULL,
    )
    cover_letter_document = models.ForeignKey(
        ApprovalDocument,
        blank=True,
        null=True,
        related_name="cover_letter_document",
        on_delete=models.SET_NULL,
    )
    sign_off_sheet = models.ForeignKey(
        ApprovalDocument,
        blank=True,
        null=True,
        related_name="sign_off_sheet",
        on_delete=models.SET_NULL,
    )
    current_proposal = models.ForeignKey(
        Proposal, related_name="approvals", null=True, on_delete=models.SET_NULL
    )
    renewal_document = models.ForeignKey(
        ApprovalDocument,
        blank=True,
        null=True,
        related_name="renewal_document",
        on_delete=models.SET_NULL,
    )
    renewal_review_notification_sent_to_assessors = models.BooleanField(default=False)
    renewal_notification_sent_to_holder = models.BooleanField(default=False)
    issue_date = models.DateTimeField()
    original_issue_date = models.DateField(auto_now_add=True)
    start_date = models.DateField()
    expiry_date = models.DateField()
    surrender_details = JSONField(blank=True, null=True)
    suspension_details = JSONField(blank=True, null=True)
    extracted_fields = JSONField(blank=True, null=True)
    cancellation_details = models.TextField(blank=True)
    extend_details = models.TextField(blank=True)
    cancellation_date = models.DateField(blank=True, null=True)
    set_to_cancel = models.BooleanField(default=False)
    set_to_suspend = models.BooleanField(default=False)
    set_to_surrender = models.BooleanField(default=False)

    # application_type = models.ForeignKey(ApplicationType, null=True, blank=True)
    renewal_count = models.PositiveSmallIntegerField(
        "Number of times an Approval has been renewed", default=0
    )
    # For leases that are migrated
    original_leaselicense_number = models.CharField(
        max_length=255, blank=True, null=True
    )
    migrated = models.BooleanField(default=False)
    record_management_number = models.CharField(max_length=100, blank=True, null=True)
    lodgement_sequence = models.IntegerField(blank=True, default=0)

    class Meta:
        app_label = "leaseslicensing"
        unique_together = ("lodgement_number", "issue_date")
        verbose_name = "Lease/License"

    @property
    def applicant(self):
        return self.current_proposal.applicant

    @property
    def holder(self):
        # TODO Is it correct to return the applicant as the approval/license holder?
        if self.is_org_applicant:
            return self.applicant.ledger_organisation_name
        elif self.is_ind_applicant:
            return self.current_proposal.proposal_applicant.full_name
        else:
            return "Applicant not yet assigned"

    @property
    def submitter(self):
        if self.current_proposal:
            return self.current_proposal.submitter
        return None

    @property
    def proxy_applicant(self):
        if self.current_proposal:
            return self.current_proposal.proxy_applicant
        return None

    @property
    def linked_applications(self):
        ids = Proposal.objects.filter(
            approval__lodgement_number=self.lodgement_number
        ).values_list("id", flat=True)
        all_linked_ids = Proposal.objects.filter(
            Q(previous_application__in=ids) | Q(id__in=ids)
        ).values_list("lodgement_number", flat=True)
        return all_linked_ids

    @property
    def applicant_type(self):
        if self.is_org_applicant:
            return "org_applicant"
        elif self.is_proxy_applicant:
            return "proxy_applicant"
        else:
            # return None
            return "submitter"

    @property
    def is_org_applicant(self):
        return (
            True
            if self.current_proposal
            and self.current_proposal.org_applicant
            and isinstance(self.current_proposal.org_applicant, Organisation)
            else False
        )

    @property
    def is_ind_applicant(self):
        return (
            True
            if self.current_proposal
            and self.current_proposal.ind_applicant
            and isinstance(
                retrieve_email_user(self.current_proposal.ind_applicant), EmailUser
            )
            else False
        )

    @property
    def is_proxy_applicant(self):
        return (
            True
            if self.current_proposal and self.current_proposal.proxy_applicant
            else False
        )

    @property
    def applicant_id(self):
        if self.is_org_applicant:
            # return self.org_applicant.organisation.id
            return self.applicant.id
        elif self.is_proxy_applicant:
            return self.proxy_applicant  # .id
        else:
            # return None
            return self.submitter

    @property
    def region(self):
        return self.current_proposal.region.name

    @property
    def district(self):
        return self.current_proposal.district.name

    @property
    def tenure(self):
        return self.current_proposal.tenure.name

    @property
    def activity(self):
        return self.current_proposal.activity

    @property
    def title(self):
        return self.current_proposal.title

    @property
    def next_id(self):
        ids = map(
            int,
            [
                re.sub("^[A-Za-z]*", "", i)
                for i in Approval.objects.all().values_list(
                    "lodgement_number", flat=True
                )
                if i
            ],
        )
        ids = list(ids)
        return max(ids) + 1 if ids else 1

    @property
    def reference(self):
        return f"L{self.id}"

    @property
    def can_reissue(self):
        return (
            self.status == self.APPROVAL_STATUS_CURRENT
            or self.status == self.APPROVAL_STATUS_SUSPENDED
            or self.status == self.APPROVAL_STATUS_CURRENT_PENDING_RENEWAL
        )

    @property
    def can_reinstate(self):
        return (
            self.status == "cancelled"
            or self.status == "suspended"
            or self.status == "surrendered"
        ) and self.can_action

    @property
    def has_outstanding_compliances(self):
        return Compliance.objects.filter(
            approval=self,
            processing_status__in=[
                Compliance.PROCESSING_STATUS_DUE,
                Compliance.PROCESSING_STATUS_WITH_ASSESSOR,
                Compliance.PROCESSING_STATUS_WITH_REFERRAL,
                Compliance.PROCESSING_STATUS_OVERDUE,
            ],
        ).exists()

    @property
    def has_outstanding_invoices(self):
        return Invoice.objects.filter(
            approval=self,
            status__in=[
                Invoice.INVOICE_STATUS_PENDING_UPLOAD_ORACLE_INVOICE,
                Invoice.INVOICE_STATUS_UNPAID,
            ],
        ).exists()

    @property
    def can_transfer(self):
        if self.has_outstanding_compliances:
            return False
        if self.has_outstanding_invoices:
            return False

        return self.status == self.APPROVAL_STATUS_CURRENT

    @property
    def allowed_assessor_ids(self):
        return user_ids_in_group(settings.GROUP_NAME_ASSESSOR)

    @property
    def allowed_assessors(self):
        emailusers = []
        for id in self.allowed_assessor_ids():
            emailuser = retrieve_email_user(id)
            emailusers.append(
                {
                    "id": id,
                    "first_name": emailuser.first_name,
                    "last_name": emailuser.last_name,
                    "email": emailuser.email,
                }
            )
        return emailusers

    @property
    def is_issued(self):
        return self.licence_number is not None and len(self.licence_number) > 0

    @property
    def can_action(self):
        if not (self.set_to_cancel or self.set_to_suspend or self.set_to_surrender):
            return True
        else:
            return False

    @property
    def can_renew(self):
        if self.status not in [
            self.APPROVAL_STATUS_CURRENT_PENDING_RENEWAL,
            self.APPROVAL_STATUS_CURRENT_PENDING_RENEWAL_REVIEW,
        ]:
            return False

        renewal_conditions = {
            "previous_application": self.current_proposal,
            "proposal_type": ProposalType.objects.get(code=PROPOSAL_TYPE_RENEWAL),
        }
        return not Proposal.objects.filter(**renewal_conditions).exists()

    # copy amend_renew() from ML?
    @property
    def can_amend(self):
        # try:
        if self.renewal_document and self.renewal_notification_sent_to_holder:
            # amend_renew = 'renew'
            return False
        else:
            amend_conditions = {
                "previous_application": self.current_proposal,
                "proposal_type": ProposalType.objects.get(code=PROPOSAL_TYPE_AMENDMENT),
            }
            proposals = Proposal.objects.filter(**amend_conditions)
            if proposals:
                if proposals.count() > 1:
                    logging.error(
                        f"Approval: {self.lodgement_number} has more than one current amendment proposals"
                    )
                return False
        return True

    @property
    def approved_by(self):
        return self.current_proposal.approved_by

    @property
    def invoicing_details(self):
        return self.current_proposal.invoicing_details

    @property
    def requirement_docs(self):
        if self.current_proposal:
            requirement_ids = (
                self.current_proposal.requirements.all()
                .exclude(is_deleted=True)
                .values_list("id", flat=True)
            )
            if requirement_ids:
                req_doc = RequirementDocument.objects.filter(
                    requirement__in=requirement_ids, visible=True
                )
                return req_doc
        else:
            logger.warning(
                f"Approval {self.lodgement_number} does not have current_proposal"
            )
        return None

    @property
    def proponent_reference_number(self):
        return self.current_proposal.proponent_reference_number

    @property
    def crown_land_rent_review_dates(self):
        review_once_every = self.current_proposal.invoicing_details.review_once_every
        if not review_once_every:
            logger.warning(
                f"Approval {self.lodgement_number} "
                "does not have a crown land rent review interval set. Returning empty list."
            )
            return []

        review_dates = []
        review_date = self.start_date + relativedelta(years=review_once_every)
        expiry_date = self.expiry_date
        while review_date < expiry_date:
            review_dates.append(review_date)
            review_date = review_date + relativedelta(years=review_once_every)

        return review_dates

    @property
    def crown_land_rent_review_due_today(self):
        today = timezone.localtime(timezone.now()).date()
        return today in self.crown_land_rent_review_dates

    def crown_land_rent_review_reminder_due_in(self, months=12):
        today = timezone.localtime(timezone.now()).date()
        return today + relativedelta(months=months) in self.crown_land_rent_review_dates

    @property
    def next_crown_land_rent_review_date(self):
        for review_date in self.crown_land_rent_review_dates:
            if review_date > timezone.now().date():
                return review_date
        return None

    def custom_cpi_entry_reminder_due_in(self, days=30):
        today = timezone.localtime(timezone.now()).date()
        return (
            today + relativedelta(days=days)
            in self.invoicing_details.invoicing_periods_start_dates
        )

    def user_has_object_permission(self, user_id):
        """Used by the secure documents api to determine if the user can view the instance and any attached documents"""
        return self.current_proposal.user_has_object_permission(user_id)

    def review_renewal(self, can_be_renewed):
        if not can_be_renewed:
            # The approval will be left in current status to expire naturally
            self.status = "current"
            self.save()
            return

        # Send email to holder letting them know that the approval is able to be renewed
        send_approval_renewal_email_notification(self)
        self.status = self.APPROVAL_STATUS_CURRENT_PENDING_RENEWAL
        self.renewal_notification_sent_to_holder = True
        self.save()

    def log_user_action(self, action, request):
        return ApprovalUserAction.log_action(self, action, request.user)

    def expire_approval(self, user):
        with transaction.atomic():
            today = timezone.localtime(timezone.now()).date()
            if self.status == "current" and self.expiry_date < today:
                self.status = "expired"
                self.save()
                send_approval_expire_email_notification(self)
                proposal = self.current_proposal
                ApprovalUserAction.log_action(
                    self,
                    ApprovalUserAction.ACTION_EXPIRE_APPROVAL.format(self.id),
                    user,
                )
                ProposalUserAction.log_action(
                    proposal,
                    ProposalUserAction.ACTION_EXPIRED_APPROVAL_.format(proposal.id),
                    user,
                )

    def approval_cancellation(self, request, details):
        with transaction.atomic():
            if request.user.id not in self.allowed_assessor_ids:
                raise ValidationError("You do not have access to cancel this approval")
            if not self.can_reissue and self.can_action:
                raise ValidationError(
                    "You cannot cancel approval if it is not current or suspended"
                )
            self.cancellation_date = details.get("cancellation_date").strftime(
                "%Y-%m-%d"
            )
            self.cancellation_details = details.get("cancellation_details")
            cancellation_date = datetime.datetime.strptime(
                self.cancellation_date, "%Y-%m-%d"
            )
            cancellation_date = cancellation_date.date()
            self.cancellation_date = cancellation_date  # test hack
            today = timezone.now().date()
            if cancellation_date <= today:
                if not self.status == "cancelled":
                    self.status = "cancelled"
                    self.set_to_cancel = False
                    send_approval_cancel_email_notification(self)
            else:
                self.set_to_cancel = True
            self.save(version_comment="status_change: Approval canceled")
            # Log proposal action
            self.log_user_action(
                ApprovalUserAction.ACTION_CANCEL_APPROVAL.format(self.id), request
            )
            # Log entry for organisation
            self.current_proposal.log_user_action(
                ProposalUserAction.ACTION_CANCEL_APPROVAL.format(
                    self.current_proposal.id
                ),
                request,
            )

    def approval_suspension(self, request, details):
        with transaction.atomic():
            if request.user.id not in self.allowed_assessor_ids:
                raise ValidationError("You do not have access to suspend this approval")
            if not self.can_reissue and self.can_action:
                raise ValidationError(
                    "You cannot suspend approval if it is not current or suspended"
                )
            if details.get("to_date"):
                to_date = details.get("to_date").strftime("%d/%m/%Y")
            else:
                to_date = ""
            self.suspension_details = {
                "from_date": details.get("from_date").strftime("%d/%m/%Y"),
                "to_date": to_date,
                "details": details.get("suspension_details"),
            }
            today = timezone.now().date()
            from_date = datetime.datetime.strptime(
                self.suspension_details["from_date"], "%d/%m/%Y"
            )
            from_date = from_date.date()
            if from_date <= today:
                if not self.status == "suspended":
                    self.status = "suspended"
                    self.set_to_suspend = False
                    self.save()
                    send_approval_suspend_email_notification(self)
            else:
                self.set_to_suspend = True
            self.save(version_comment="status_change: Approval suspended")
            # Log approval action
            self.log_user_action(
                ApprovalUserAction.ACTION_SUSPEND_APPROVAL.format(self.id), request
            )
            # Log entry for proposal
            self.current_proposal.log_user_action(
                ProposalUserAction.ACTION_SUSPEND_APPROVAL.format(
                    self.current_proposal.id
                ),
                request,
            )

    def reinstate_approval(self, request):
        with transaction.atomic():
            if request.user.id not in self.allowed_assessor_ids:
                raise ValidationError(
                    "You do not have access to reinstate this approval"
                )
            if not self.can_reinstate:
                # if not self.status == 'suspended':
                raise ValidationError("You cannot reinstate approval at this stage")
            today = timezone.now().date()
            if not self.can_reinstate and self.expiry_date >= today:
                # if not self.status == 'suspended' and self.expiry_date >= today:
                raise ValidationError("You cannot reinstate approval at this stage")
            if self.status == "cancelled":
                self.cancellation_details = ""
                self.cancellation_date = None
            if self.status == "surrendered":
                self.surrender_details = {}
            if self.status == "suspended":
                self.suspension_details = {}

            self.status = "current"
            self.renewal_review_notification_sent_to_assessors = (
                False  # Should be able to renew again
            )
            # self.suspension_details = {}
            self.save(version_comment="status_change: Approval reinstated")
            send_approval_reinstate_email_notification(self, request)
            # Log approval action
            self.log_user_action(
                ApprovalUserAction.ACTION_REINSTATE_APPROVAL.format(self.id),
                request,
            )
            # Log entry for proposal
            self.current_proposal.log_user_action(
                ProposalUserAction.ACTION_REINSTATE_APPROVAL.format(
                    self.current_proposal.id
                ),
                request,
            )

    def approval_surrender(self, request, details):
        with transaction.atomic():
            orgs_for_user = get_organisation_ids_for_user(request.user.id)
            if self.applicant_id not in orgs_for_user:
                if (
                    request.user.id not in self.allowed_assessor_ids
                    and not is_customer(request)
                ):
                    raise ValidationError(
                        "You do not have access to surrender this approval"
                    )
            if not self.can_reissue and self.can_action:
                raise ValidationError(
                    "You cannot surrender approval if it is not current or suspended"
                )
            self.surrender_details = {
                "surrender_date": details.get("surrender_date").strftime("%d/%m/%Y"),
                "details": details.get("surrender_details"),
            }
            today = timezone.now().date()
            surrender_date = datetime.datetime.strptime(
                self.surrender_details["surrender_date"], "%d/%m/%Y"
            )
            surrender_date = surrender_date.date()
            if surrender_date <= today:
                if not self.status == "surrendered":
                    self.status = "surrendered"
                    self.set_to_surrender = False
                    self.save()
                    send_approval_surrender_email_notification(self)
            else:
                self.set_to_surrender = True
            self.save(version_comment="status_change: Approval surrendered")
            # Log approval action
            self.log_user_action(
                ApprovalUserAction.ACTION_SURRENDER_APPROVAL.format(self.id),
                request,
            )
            # Log entry for proposal
            self.current_proposal.log_user_action(
                ProposalUserAction.ACTION_SURRENDER_APPROVAL.format(
                    self.current_proposal.id
                ),
                request,
            )

    @property
    def as_related_item(self):
        related_item = RelatedItem(
            identifier=self.related_item_identifier,
            model_name=self._meta.verbose_name,
            descriptor=self.related_item_descriptor,
            action_url=f'<a href=/internal/approval/{self.id} target="_blank">Open</a>',
            type="lease_license",
        )
        return related_item

    @property
    def related_item_identifier(self):
        return self.lodgement_number

    @property
    def related_item_descriptor(self):
        """
        Returns this license's expiry date as item description
        """

        return self.expiry_date


class ApprovalLogEntry(CommunicationsLogEntry):
    approval = models.ForeignKey(
        Approval, related_name="comms_logs", on_delete=models.CASCADE
    )

    class Meta:
        app_label = "leaseslicensing"

    def save(self, **kwargs):
        # save the reference if the reference not provided
        if not self.reference:
            self.reference = self.approval.id
        super().save(**kwargs)


class ApprovalLogDocument(Document):
    log_entry = models.ForeignKey(
        "ApprovalLogEntry",
        related_name="documents",
        null=True,
        on_delete=models.CASCADE,
    )
    _file = SecureFileField(
        upload_to=update_approval_comms_log_filename, null=True, max_length=512
    )

    class Meta:
        app_label = "leaseslicensing"


class ApprovalCancellationDocument(Document):
    approval = models.ForeignKey(
        Approval,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approval_cancellation_documents",
    )
    input_name = models.CharField(max_length=255, null=True, blank=True)
    _file = SecureFileField(
        upload_to=update_approval_cancellation_doc_filename, max_length=512
    )

    class Meta:
        app_label = "leaseslicensing"


class ApprovalSurrenderDocument(Document):
    approval = models.ForeignKey(
        Approval,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approval_surrender_documents",
    )
    input_name = models.CharField(max_length=255, null=True, blank=True)
    _file = SecureFileField(
        upload_to=update_approval_surrender_doc_filename, max_length=512
    )

    class Meta:
        app_label = "leaseslicensing"


class ApprovalSuspensionDocument(Document):
    approval = models.ForeignKey(
        Approval,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approval_suspension_documents",
    )
    input_name = models.CharField(max_length=255, null=True, blank=True)
    _file = SecureFileField(
        upload_to=update_approval_suspension_doc_filename, max_length=512
    )

    class Meta:
        app_label = "leaseslicensing"


class ApprovalTransfer(LicensingModelVersioned):
    MODEL_PREFIX = "LT"

    APPROVAL_TRANSFER_STATUS_DRAFT = "draft"
    APPROVAL_TRANSFER_STATUS_CANCELLED = "cancelled"
    APPROVAL_TRANSFER_STATUS_PENDING = "pending"
    APPROVAL_TRANSFER_STATUS_DECLINED = "declined"
    APPROVAL_TRANSFER_STATUS_ACCEPTED = "accepted"

    APPROVAL_TRANSFER_STATUS_CHOICES = (
        (APPROVAL_TRANSFER_STATUS_DRAFT, "Draft"),
        (APPROVAL_TRANSFER_STATUS_CANCELLED, "Cancelled"),
        (APPROVAL_TRANSFER_STATUS_PENDING, "Pending"),
        (APPROVAL_TRANSFER_STATUS_DECLINED, "Declined"),
        (APPROVAL_TRANSFER_STATUS_ACCEPTED, "Accepted"),
    )

    lodgement_number = models.CharField(max_length=9, unique=True)
    processing_status = models.CharField(
        max_length=40,
        choices=APPROVAL_TRANSFER_STATUS_CHOICES,
        default=APPROVAL_TRANSFER_STATUS_DRAFT,
        null=False,
        blank=False,
    )
    approval = models.ForeignKey(
        Approval,
        null=True,
        blank=False,
        on_delete=models.PROTECT,
        related_name="transfer",
    )
    transferee = models.IntegerField(null=True, blank=True)

    class Meta:
        app_label = "leaseslicensing"
        ordering = ("-lodgement_number",)


class ApprovalUserAction(UserAction):
    ACTION_CREATE_APPROVAL = "Create Lease/License {}"
    ACTION_UPDATE_APPROVAL = "Update Lease/License {}"
    ACTION_UPDATE_APPROVAL_INVOICING_DETAILS = (
        "Update Lease/License {} Invoicing Details. Comment text: {}"
    )
    ACTION_REVIEW_INVOICING_DETAILS_BASE_FEE_APPROVAL = "Base Fee changed from {} to {}"
    ACTION_EXPIRE_APPROVAL = "Expire Lease/License {}"
    ACTION_CANCEL_APPROVAL = "Cancel Lease/License {}"
    ACTION_EXTEND_APPROVAL = "Extend Lease/License {}"
    ACTION_SUSPEND_APPROVAL = "Suspend Lease/License {}"
    ACTION_REINSTATE_APPROVAL = "Reinstate Lease/License {}"
    ACTION_SURRENDER_APPROVAL = "Surrender Lease/License {}"
    ACTION_RENEW_APPROVAL = "Create Renewal Application for Lease/License {}"
    ACTION_AMEND_APPROVAL = "Create Amendment Application for Lease/License {}"
    ACTION_AD_HOC_INVOICE_GENERATED_APPROVAL = (
        "Ad-hoc Invoice {} generated for Lease/License {}"
    )

    class Meta:
        app_label = "leaseslicensing"
        ordering = ("-when",)

    @classmethod
    def log_action(cls, approval, action, user):
        return cls.objects.create(approval=approval, who=user.id, what=str(action))

    approval = models.ForeignKey(
        Approval, related_name="action_logs", on_delete=models.CASCADE
    )


@receiver(pre_delete, sender=Approval)
def delete_documents(sender, instance, *args, **kwargs):
    for document in instance.documents.all():
        try:
            document.delete()
        except ProtectedError:
            logger.info(f"Document: {document} is protected. Unable to delete.")
