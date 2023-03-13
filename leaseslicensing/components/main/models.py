from __future__ import unicode_literals
from reversion.models import Version
import os

from django.db import models
from django.db.models import Q
from django.dispatch import receiver
from django.db.models.signals import pre_delete

# from django.utils.encoding import python_2_unicode_compatible
from django.core.exceptions import ValidationError

# from ledger.accounts.models import EmailUser, Document, RevisionedMixin
from ledger_api_client.ledger_models import (
    EmailUserRO as EmailUser,
    BaseAddress,
)  # , RevisionedMixin

# from django.contrib.postgres.fields.jsonb import JSONField
from django.db.models import JSONField
from leaseslicensing import settings
from leaseslicensing.ledger_api_utils import retrieve_email_user


## TODO: remove ledger models

##@python_2_unicode_compatible
# class Organisation(models.Model):
#    """This model represents the details of a company or other organisation.
#    Management of these objects will be delegated to 0+ EmailUsers.
#    """
#    name = models.CharField(max_length=128, unique=True)
#    abn = models.CharField(max_length=50, null=True, blank=True, verbose_name='ABN')
#    # TODO: business logic related to identification file upload/changes.
#    identification = models.FileField(upload_to='%Y/%m/%d', null=True, blank=True)
#    postal_address = models.ForeignKey('OrganisationAddress', related_name='org_postal_address', blank=True, null=True, on_delete=models.SET_NULL)
#    billing_address = models.ForeignKey('OrganisationAddress', related_name='org_billing_address', blank=True, null=True, on_delete=models.SET_NULL)
#    email = models.EmailField(blank=True, null=True,)
#    trading_name = models.CharField(max_length=256, null=True, blank=True)
#
#    def upload_identification(self, request):
#        with transaction.atomic():
#            self.identification = request.data.dict()['identification']
#            self.save()
#
#    def __str__(self):
#        return self.name
#
#    class Meta:
#        #abstract = True
#        managed = False
#
# class OrganisationAddress(BaseAddress):
#    organisation = models.ForeignKey(Organisation, null=True,blank=True, related_name='adresses', on_delete=models.CASCADE)
#    class Meta:
#        verbose_name_plural = 'organisation addresses'
#        unique_together = ('organisation','hash')
#
#    class Meta:
#        #abstract = True
#        managed = False

#####


class MapLayer(models.Model):
    display_name = models.CharField(max_length=100, blank=True, null=True)
    layer_name = models.CharField(max_length=200, blank=True, null=True)
    option_for_internal = models.BooleanField(default=True)
    option_for_external = models.BooleanField(default=True)
    display_all_columns = models.BooleanField(default=False)
    transparency = models.PositiveSmallIntegerField(
        default=50
    )  # Transparency of the layer. 0 means solid.  100 means fully transparent.

    class Meta:
        app_label = "leaseslicensing"
        verbose_name = "map layer"

    def __str__(self):
        return "{0}, {1}".format(self.display_name, self.layer_name)

    @property
    def column_names(self):
        column_names = []
        for column in self.columns.all():
            column_names.append(column.name)
        return ",".join(column_names)


class MapColumn(models.Model):
    map_layer = models.ForeignKey(
        MapLayer,
        null=True,
        blank=True,
        related_name="columns",
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=100, blank=True, null=True)
    option_for_internal = models.BooleanField(default=True)
    option_for_external = models.BooleanField(default=True)

    class Meta:
        app_label = "leaseslicensing"
        verbose_name = "map column"

    def __str__(self):
        return "{0}, {1}".format(self.map_layer, self.name)


class RevisionedMixin(models.Model):
    """
    A model tracked by reversion through the save method.
    """

    def save(self, **kwargs):
        from reversion import revisions

        if kwargs.pop("no_revision", False):
            super(RevisionedMixin, self).save(**kwargs)
        else:
            with revisions.create_revision():
                if "version_user" in kwargs:
                    revisions.set_user(kwargs.pop("version_user", None))
                if "version_comment" in kwargs:
                    # Increment the lodgement sequence on every save with a version comment.
                    # Versions are only commented on concluding saves (e.g. on submit),
                    # typically when the status changes, i.e. the first save of a new status
                    # is also the first version to use the incremented sequence.
                    if hasattr(self, "lodgement_sequence"):
                        self.lodgement_sequence += 1
                    revisions.set_comment(kwargs.pop("version_comment", ""))
                super(RevisionedMixin, self).save(**kwargs)

    def reverse_fk_versions(self, reverse_attr, **kwargs):
        """
        Returns a list of a model's one-to-many foreign key relation versions
        selected by filter expression. E.g. because Proposal is a property of
        ProposalGeometry, there is a 1:N relation Proposal -> ProposalGeometry
        and a reverse foreign key lookup of proposal geometries would always
        return all geometries belonging to a proposal id even though some did
        not exist at a specific version of the proposal.
        This function returns only those versions that existed a certain revision
        id.

        Args:
            reverse_attr (str):
                The attribute in the model to query for
            lookup (dict, optional):
                The filter expression to apply, e.g. `{'__lte':1234}`,
                Defaults to empty dict `{}`, i.e. no filter applies.
                Does not get used when `lookup_filter=` is used
            lookup_filter (Q-expression, optional):
                A Q-expression to filter `reverse_attr` queryset

        Examples:
            - geometry_versions = model_instance.reverse_fk_versions(
                "proposalgeometry",
                lookup={"__lte": 1234})
            - geometry_versions = model_instance.reverse_fk_versions(
                "proposalgeometry",
                lookup_filter=Q(revision_id__lte=1234)), i.e. can
                add negation and more complex expressions
        """

        # How to filter the revision table
        lookup = kwargs.get("lookup", {})
        lookup_filter = kwargs.get("lookup_filter", None)
        if not lookup_filter:
            # The lookup filter to apply
            lookup_filter = Q(**{f"revision_id{k}":f"{v}" for k,v in iter(lookup.items())})

        # Reverse foreign key queryset
        if hasattr(self, reverse_attr):
            reverse_fk_qs = getattr(self, reverse_attr).all()
        else:
            raise ValidationError(f"{self.__class__.__name__} has no attribute {reverse_attr}")

        # A list of filtered attribute versions
        rfk_versions = []
        for obj in reverse_fk_qs:
            version = [p for p in Version.objects.get_for_object(
                obj).select_related(
                'revision').filter(lookup_filter)
                ]
            rfk_versions += version

        return list(set(rfk_versions))

    @property
    def created_date(self):

        # return revisions.get_for_object(self).last().revision.date_created
        return Version.objects.get_for_object(self).last().revision.date_created

    @property
    def modified_date(self):

        # return revisions.get_for_object(self).first().revision.date_created
        return Version.objects.get_for_object(self).first().revision.date_created

    class Meta:
        abstract = True


# @python_2_unicode_compatible
class RequiredDocument(models.Model):
    question = models.TextField(blank=False)

    class Meta:
        app_label = "leaseslicensing"

    def __str__(self):
        return self.question


# @python_2_unicode_compatible
class ApplicationType(models.Model):
    name = models.CharField(
        max_length=64, unique=True, choices=settings.APPLICATION_TYPES
    )
    order = models.PositiveSmallIntegerField(default=0)
    visible = models.BooleanField(default=True)

    application_fee = models.DecimalField(
        "Application Fee", max_digits=6, decimal_places=2, null=True
    )
    oracle_code_application = models.CharField(max_length=50)
    oracle_code_licence = models.CharField(max_length=50)
    is_gst_exempt = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "name"]
        app_label = "leaseslicensing"

    @staticmethod
    def get_application_type_by_name(name):
        try:
            return ApplicationType.objects.get(name=name)
        except:
            return None

    @property
    def name_display(self):
        return self.get_name_display()

    @property
    def confirmation_text(self):
        text = ""
        if self.name == "registration_of_interest":
            text = "Registration of Interest"
        if self.name == "lease_licence":
            text = "Lease or Licence"
        return text

    def __str__(self):
        return self.name


# @python_2_unicode_compatible
class OracleCode(models.Model):
    CODE_TYPE_CHOICES = (
        (
            settings.APPLICATION_TYPE_REGISTRATION_OF_INTEREST,
            settings.APPLICATION_TYPE_REGISTRATION_OF_INTEREST,
        ),
        (
            settings.APPLICATION_TYPE_LEASE_LICENCE,
            settings.APPLICATION_TYPE_LEASE_LICENCE,
        ),
    )
    code_type = models.CharField(
        "Application Type",
        max_length=64,
        choices=CODE_TYPE_CHOICES,
        default=CODE_TYPE_CHOICES[0][0],
    )
    code = models.CharField(max_length=50, blank=True)
    archive_date = models.DateField(null=True, blank=True)

    class Meta:
        app_label = "leaseslicensing"

    def __str__(self):
        return "{} - {}".format(self.code_type, self.code)


# @python_2_unicode_compatible
class Question(models.Model):
    CORRECT_ANSWER_CHOICES = (
        ("answer_one", "Answer one"),
        ("answer_two", "Answer two"),
        ("answer_three", "Answer three"),
        ("answer_four", "Answer four"),
    )
    question_text = models.TextField(blank=False)
    answer_one = models.CharField(max_length=200, blank=True)
    answer_two = models.CharField(max_length=200, blank=True)
    answer_three = models.CharField(max_length=200, blank=True)
    answer_four = models.CharField(max_length=200, blank=True)
    # answer_five = models.CharField(max_length=200, blank=True)
    correct_answer = models.CharField(
        "Correct Answer",
        max_length=40,
        choices=CORRECT_ANSWER_CHOICES,
        default=CORRECT_ANSWER_CHOICES[0][0],
    )
    application_type = models.ForeignKey(
        ApplicationType, null=True, blank=True, on_delete=models.SET_NULL
    )

    class Meta:
        # ordering = ['name']
        app_label = "leaseslicensing"

    def __str__(self):
        return self.question_text

    @property
    def correct_answer_value(self):
        return getattr(self, self.correct_answer)


# @python_2_unicode_compatible
class UserAction(models.Model):
    # who = models.ForeignKey(EmailUser, null=True, blank=True, on_delete=models.SET_NULL)
    who = models.IntegerField()  # EmailUserRO
    when = models.DateTimeField(null=False, blank=False, auto_now_add=True)
    what = models.TextField(blank=False)

    def __str__(self):
        return "{what} ({who} at {when})".format(
            what=self.what, who=self.who, when=self.when
        )

    class Meta:
        abstract = True
        app_label = "leaseslicensing"


class CommunicationsLogEntry(models.Model):
    TYPE_CHOICES = [
        ("email", "Email"),
        ("phone", "Phone Call"),
        ("mail", "Mail"),
        ("person", "In Person"),
        ("onhold", "On Hold"),
        ("onhold_remove", "Remove On Hold"),
        ("with_qaofficer", "With QA Officer"),
        ("with_qaofficer_completed", "QA Officer Completed"),
        ("referral_complete", "Referral Completed"),
    ]
    DEFAULT_TYPE = TYPE_CHOICES[0][0]

    # to = models.CharField(max_length=200, blank=True, verbose_name="To")
    to = models.TextField(blank=True, verbose_name="To")
    fromm = models.CharField(max_length=200, blank=True, verbose_name="From")
    # cc = models.CharField(max_length=200, blank=True, verbose_name="cc")
    cc = models.TextField(blank=True, verbose_name="cc")

    type = models.CharField(max_length=35, choices=TYPE_CHOICES, default=DEFAULT_TYPE)
    reference = models.CharField(max_length=100, blank=True)
    subject = models.CharField(
        max_length=200, blank=True, verbose_name="Subject / Description"
    )
    text = models.TextField(blank=True)

    # customer = models.ForeignKey(EmailUser, null=True, related_name='+', on_delete=models.SET_NULL)
    customer = models.IntegerField(null=True)  # EmailUserRO
    # staff = models.ForeignKey(EmailUser, null=True, related_name='+', on_delete=models.SET_NULL)
    staff = models.IntegerField()  # EmailUserRO

    created = models.DateTimeField(auto_now_add=True, null=False, blank=False)

    class Meta:
        app_label = "leaseslicensing"


# @python_2_unicode_compatible
class Document(models.Model):
    name = models.CharField(
        max_length=255, blank=True, verbose_name="name", help_text=""
    )
    description = models.TextField(blank=True, verbose_name="description", help_text="")
    uploaded_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "leaseslicensing"
        abstract = True

    @property
    def path(self):
        # return self.file.path
        # return self._file.path
        # comment above line to fix the error "The '_file' attribute has no file associated with it." when adding comms log entry.
        if self._file:
            return self._file.path
        else:
            return ""

    @property
    def filename(self):
        return os.path.basename(self.path)

    def __str__(self):
        return self.name or self.filename


class GlobalSettings(models.Model):
    keys = (
        # ('credit_facility_link', 'Credit Facility Link'),
        # ('deed_poll', 'Deed poll'),
        # ('deed_poll_filming', 'Deed poll Filming'),
        # ('deed_poll_event', 'Deed poll Event'),
        # ('online_training_document', 'Online Training Document'),
        # ('park_finder_link', 'Park Finder Link'),
        # ('fees_and_charges', 'Fees and charges link'),
        # ('event_fees_and_charges', 'Event Fees and charges link'),
        # ('commercial_filming_handbook', 'Commercial Filming Handbook link'),
        # ('park_stay_link', 'Park Stay Link'),
        # ('event_traffic_code_of_practice', 'Event traffic code of practice'),
        # ('trail_section_map', 'Trail section map'),
        # ('dwer_application_form', 'DWER Application Form'),
    )
    key = models.CharField(
        max_length=255,
        choices=keys,
        blank=False,
        null=False,
    )
    value = models.CharField(max_length=255)

    class Meta:
        app_label = "leaseslicensing"
        verbose_name_plural = "Global Settings"


# @python_2_unicode_compatible
class SystemMaintenance(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def duration(self):
        """Duration of system maintenance (in mins)"""
        return (
            int((self.end_date - self.start_date).total_seconds() / 60.0)
            if self.end_date and self.start_date
            else ""
        )
        # return (datetime.now(tz=tz) - self.start_date).total_seconds()/60.

    duration.short_description = "Duration (mins)"

    class Meta:
        app_label = "leaseslicensing"
        verbose_name_plural = "System maintenance"

    def __str__(self):
        return "System Maintenance: {} ({}) - starting {}, ending {}".format(
            self.name, self.description, self.start_date, self.end_date
        )


class UserSystemSettings(models.Model):
    one_row_per_park = models.BooleanField(
        default=False
    )  # Setting for user if they want to see Payment (Park Entry Fees Dashboard) by one row per park or one row per booking
    # user = models.OneToOneField(EmailUser, related_name='system_settings', on_delete=models.CASCADE)
    user = models.IntegerField(unique=True)  # EmailUserRO
    event_training_completed = models.BooleanField(default=False)
    event_training_date = models.DateField(blank=True, null=True)

    class Meta:
        app_label = "leaseslicensing"
        verbose_name_plural = "User System Settings"

# Not ready for use
class SecurityGroup(models.Model):

    #name = models.CharField(max_length=150, unique=True)
    name = models.CharField(
        max_length=200,
        choices=settings.GROUP_NAME_CHOICES)
    #group_email = models.CharField(max_length=255, blank=True)

    class Meta:
        app_label = 'leaseslicensing'

    def __str__(self):
        return self.name

    def get_members(self):
        return [retrieve_email_user(member.emailuser) for member in self.securitygroupmembership_set.all()]

    def add_member(self, user_id):
        SecurityGroupMembership.objects.create(group=self,emailuser=user_id)


# Not ready for use
class SecurityGroupMembership(models.Model):
    group = models.ForeignKey(SecurityGroup, on_delete=models.PROTECT)
    #emailuser = models.ForeignKey(EmailUser, on_delete=models.PROTECT, blank=True, null=True, db_constraint=False)
    emailuser = models.IntegerField(null=True)  # EmailUserRO
    active = models.BooleanField(default=True)

    class Meta:
        app_label = 'leaseslicensing'

    def __str__(self):
        return str(self.group)


class TemporaryDocumentCollection(models.Model):

    class Meta:
        app_label = 'leaseslicensing'


class TemporaryDocument(Document):
    temp_document_collection = models.ForeignKey(
        TemporaryDocumentCollection,
        related_name='documents',
        on_delete=models.CASCADE,
    )
    _file = models.FileField(max_length=255)

    class Meta:
        app_label = 'leaseslicensing'


# import reversion
# reversion.register(Region, follow=['districts'])
# reversion.register(District, follow=['parks'])
##reversion.register(AccessType)
# reversion.register(AccessType, follow=['park_set', 'proposalparkaccess_set', 'vehicles'])
# reversion.register(ActivityType)
# reversion.register(ActivityCategory, follow=['activities'])
##reversion.register(Activity, follow=['park_set', 'zone_set', 'trail_set', 'requireddocument_set'])
# reversion.register(Activity, follow=['park_set', 'zone_set', 'trail_set', 'requireddocument_set', 'proposalparkactivity_set','proposalparkzoneactivity_set', 'proposaltrailsectionactivity_set'])
##reversion.register(Park, follow=['zones', 'requireddocument_set', 'proposals', 'park_entries', 'bookings'])
# reversion.register(Park, follow=['zones', 'requireddocument_set', 'proposals'])
# reversion.register(Zone, follow=['proposal_zones'])
# reversion.register(Trail, follow=['sections', 'proposals'])
# reversion.register(Section, follow=['proposal_trails'])
# reversion.register(RequiredDocument)
# reversion.register(ApplicationType, follow=['tenure_app_types', 'helppage_set'])
# reversion.register(ActivityMatrix)
# reversion.register(Tenure)
# reversion.register(Question)
# reversion.register(UserAction)
# reversion.register(CommunicationsLogEntry)
# reversion.register(Document)
# reversion.register(SystemMaintenance)

# Everything `django-reversion` related below
import reversion

# main
reversion.register(ApplicationType, follow=[])

# approval
from leaseslicensing.components.approvals.models import (Approval, ApprovalSubType,
                                                         ApprovalType, ApprovalTypeDocumentType,
                                                         ApprovalTypeDocumentTypeOnApprovalType,
                                                         ApprovalDocument
                                                         )
reversion.register(Approval, follow=["licence_document",
                                     "cover_letter_document",
                                     "replaced_by",
                                     "current_proposal",
                                     "renewal_document",
                                     "org_applicant"
                                     ])
reversion.register(ApprovalSubType)
reversion.register(ApprovalType, follow=["approvaltypedocumenttypes"])
reversion.register(ApprovalTypeDocumentType)
reversion.register(ApprovalTypeDocumentTypeOnApprovalType)
reversion.register(ApprovalDocument)

# bookings
from leaseslicensing.components.bookings.models import (Payment, BookingInvoice,
                                                        Booking,
                                                        ApplicationFee, ApplicationFeeInvoice,
                                                        ComplianceFeeInvoice, ComplianceFee
                                                        )

reversion.register(Payment)
reversion.register(BookingInvoice, follow=["booking"])
reversion.register(Booking)
reversion.register(ApplicationFee)
reversion.register(ApplicationFeeInvoice, follow=["application_fee"])
reversion.register(ComplianceFeeInvoice, follow=["compliance_fee"])
reversion.register(ComplianceFee)

# proposal
from leaseslicensing.components.proposals.models import (Proposal, ProposalType, Organisation,
                                                         ProposalDocument, CompetitiveProcess,
                                                         ShapefileDocument, AdditionalDocumentType,
                                                         ApplicationFeeDiscount, ProposalStandardRequirement,
                                                         Referral, ReferralDocument, ProposalRequirement,
                                                         ProposalStandardRequirement, ReferralRecipientGroup,
                                                         SectionChecklist, ChecklistQuestion,
                                                         ProposalAssessment, ProposalAssessmentAnswer,
                                                         ProposalGeometry
                                                         )
reversion.register(ProposalType)
reversion.register(Organisation)
reversion.register(ProposalDocument)
reversion.register(CompetitiveProcess)
reversion.register(ShapefileDocument, follow=["proposal"])
reversion.register(AdditionalDocumentType)
reversion.register(ApplicationFeeDiscount, follow=["proposal"])
reversion.register(ProposalStandardRequirement, follow=["application_type"])
reversion.register(Referral, follow=["proposal", "document"])
reversion.register(ReferralDocument, follow=["referral"])
reversion.register(ProposalRequirement, follow=["proposal",
                                                "standard_requirement",
                                                "copied_from",
                                                "referral_group"])
reversion.register(ReferralRecipientGroup)
reversion.register(SectionChecklist, follow=["application_type"])
reversion.register(ChecklistQuestion, follow=["section_checklist"])
reversion.register(ProposalAssessment, follow=["proposal",
                                               "referral"])
reversion.register(ProposalAssessmentAnswer, follow=["checklist_question",
                                                     "proposal_assessment"])
reversion.register(Proposal, follow=["application_type",
                                     "proposal_type",
                                     "org_applicant",
                                     "approval",
                                     "previous_application",
                                     "approval_level_document",
                                     "generated_proposal",
                                     "originating_competitive_process",
                                    #  "proposalgeometry"
                                     ])
reversion.register(ProposalGeometry, follow=["proposal"])
