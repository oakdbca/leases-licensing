from django.conf import settings
from django.utils import timezone
from ledger_api_client.ledger_models import EmailUserRO as EmailUser
from rest_framework import serializers

from leaseslicensing.components.approvals.models import (
    Approval,
    ApprovalDocument,
    ApprovalLogEntry,
    ApprovalUserAction,
)
from leaseslicensing.components.main.serializers import (
    CommunicationLogEntrySerializer,
    EmailUserSerializer,
)
from leaseslicensing.components.main.utils import get_secure_file_url
from leaseslicensing.components.organisations.models import Organisation
from leaseslicensing.components.organisations.serializers import OrganisationSerializer
from leaseslicensing.components.users.serializers import UserSerializer
from leaseslicensing.helpers import is_approver, is_assessor


class ApprovalPaymentSerializer(serializers.ModelSerializer):
    # proposal = serializers.SerializerMethodField(read_only=True)
    org_applicant = serializers.SerializerMethodField(read_only=True)
    bpay_allowed = serializers.SerializerMethodField(read_only=True)
    monthly_invoicing_allowed = serializers.SerializerMethodField(read_only=True)
    other_allowed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Approval
        fields = (
            "lodgement_number",
            "current_proposal",
            "expiry_date",
            "org_applicant",
            "bpay_allowed",
            "monthly_invoicing_allowed",
            "other_allowed",
        )
        read_only_fields = (
            "lodgement_number",
            "current_proposal",
            "expiry_date",
            "org_applicant",
            "bpay_allowed",
            "monthly_invoicing_allowed",
            "other_allowed",
        )

    def get_org_applicant(self, obj):
        return obj.org_applicant.name if obj.org_applicant else None

    def get_bpay_allowed(self, obj):
        return obj.bpay_allowed

    def get_monthly_invoicing_allowed(self, obj):
        return obj.monthly_invoicing_allowed

    def get_other_allowed(self, obj):
        return settings.OTHER_PAYMENT_ALLOWED

    # def get_monthly_invoicing_period(self,obj):
    #    return obj.monthly_invoicing_period

    # def get_monthly_payment_due_period(self,obj):
    #    return obj.monthly_payment_due_period

    # def get_proposal_id(self,obj):
    #    return obj.current_proposal_id


class _ApprovalPaymentSerializer(serializers.ModelSerializer):
    applicant = serializers.SerializerMethodField(read_only=True)
    applicant_type = serializers.SerializerMethodField(read_only=True)
    applicant_id = serializers.SerializerMethodField(read_only=True)
    status = serializers.CharField(source="get_status_display")
    title = serializers.CharField(source="current_proposal.title")
    application_type = serializers.SerializerMethodField(read_only=True)
    land_parks = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Approval
        fields = (
            "id",
            "lodgement_number",
            "current_proposal",
            "title",
            "issue_date",
            "start_date",
            "expiry_date",
            "applicant",
            "applicant_type",
            "applicant_id",
            "status",
            "cancellation_date",
            "application_type",
            "land_parks",
        )

    def get_application_type(self, obj):
        if obj.current_proposal.application_type:
            return obj.current_proposal.application_type.name
        return None

    def get_applicant(self, obj):
        return (
            obj.applicant.name
            if isinstance(obj.applicant, Organisation)
            else obj.applicant
        )

    def get_applicant_type(self, obj):
        return obj.applicant_type

    def get_applicant_id(self, obj):
        return obj.applicant_id

    def get_land_parks(self, obj):
        return None  # obj.current_proposal.land_parks
        # return AuthorSerializer(obj.author).data
        # if obj.current_proposal.land_parks:
        #    return ProposalParkSerializer(obj.current_proposal.land_parks).data
        # return None


class ApprovalSerializer(serializers.ModelSerializer):
    applicant_type = serializers.SerializerMethodField(read_only=True)
    applicant_id = serializers.SerializerMethodField(read_only=True)
    licence_document = serializers.SerializerMethodField()
    # renewal_document = serializers.SerializerMethodField(read_only=True)
    status = serializers.CharField(source="get_status_display")
    application_type = serializers.SerializerMethodField(read_only=True)
    linked_applications = serializers.SerializerMethodField(read_only=True)
    can_renew = serializers.SerializerMethodField()
    is_assessor = serializers.SerializerMethodField()
    is_approver = serializers.SerializerMethodField()
    requirement_docs = serializers.SerializerMethodField()
    submitter = serializers.SerializerMethodField()
    holder = serializers.SerializerMethodField()
    holder_obj = serializers.SerializerMethodField()
    groups_comma_list = serializers.SerializerMethodField(read_only=True)
    site_name = serializers.CharField(
        source="current_proposal.site_name.name", allow_null=True, read_only=True
    )
    groups_names_list = serializers.ListField(
        source="current_proposal.groups_names_list", read_only=True
    )
    categories_list = serializers.ListField(
        source="current_proposal.categories_list", read_only=True
    )

    class Meta:
        model = Approval
        fields = (
            "id",
            "lodgement_number",
            "linked_applications",
            "licence_document",
            "replaced_by",
            "current_proposal",
            "tenure",
            "renewal_notification_sent_to_holder",
            "issue_date",
            "original_issue_date",
            "start_date",
            "expiry_date",
            "surrender_details",
            "suspension_details",
            "applicant_type",
            "applicant_id",
            "holder",
            "holder_obj",
            "extracted_fields",
            "status",
            "reference",
            "can_reissue",
            "cancellation_date",
            "cancellation_details",
            "can_action",
            "set_to_cancel",
            "set_to_surrender",
            "set_to_suspend",
            "can_renew",
            "can_amend",
            "can_reinstate",
            "application_type",
            "original_leaselicense_number",
            "migrated",
            "is_assessor",
            "is_approver",
            "requirement_docs",
            "submitter",
            "groups_comma_list",
            "groups_names_list",
            "categories_list",
            "site_name",
            "record_management_number",
        )
        # the serverSide functionality of datatables is such that only columns that have
        # field 'data' defined are requested from the serializer. We
        # also require the following additional fields for some of the mRender functions
        datatables_always_serialize = (
            "id",
            "status",
            "reference",
            "lodgement_number",
            "linked_applications",
            "licence_document",
            "start_date",
            "expiry_date",
            "holder",
            "holder_obj",
            "can_reissue",
            "can_action",
            "can_reinstate",
            "can_amend",
            "can_renew",
            "set_to_cancel",
            "set_to_suspend",
            "set_to_surrender",
            "current_proposal",
            "renewal_notification_sent_to_holder",
            "application_type",
            "migrated",
            "is_assessor",
            "is_approver",
            "requirement_docs",
            "submitter",
            "groups_comma_list",
        )

    def get_licence_document(self, obj):
        if not obj.licence_document or not obj.licence_document._file:
            return None
        return get_secure_file_url(obj.licence_document, "_file")

    def get_submitter(self, obj):
        user = EmailUser.objects.get(id=obj.submitter)
        return EmailUserSerializer(user).data

    def get_linked_applications(self, obj):
        return obj.linked_applications

    def get_renewal_document(self, obj):
        if obj.renewal_document and obj.renewal_document._file:
            return obj.renewal_document._file.url
        return None

    def get_application_type(self, obj):
        if obj.current_proposal:
            if obj.current_proposal.application_type:
                return obj.current_proposal.application_type.name_display
        return None

    def get_holder(self, obj):
        if isinstance(obj.applicant, Organisation):
            return obj.applicant.ledger_organisation_name
        elif isinstance(obj.applicant, EmailUser):
            return f"{obj.applicant.first_name} {obj.applicant.last_name}"
        else:
            return "Applicant not yet assigned"

    def get_applicant_type(self, obj):
        if isinstance(obj.applicant, Organisation):
            return "organisation"
        elif isinstance(obj.applicant, EmailUser):
            return "individual"
        else:
            return "Applicant not yet assigned"

    def get_applicant_id(self, obj):
        return obj.applicant_id

    def get_holder_obj(self, obj):
        if isinstance(obj.applicant, Organisation):
            return OrganisationSerializer(obj.applicant).data
        return UserSerializer(obj.applicant).data

    def get_can_renew(self, obj):
        return obj.can_renew

    def get_is_assessor(self, obj):
        request = self.context["request"]
        return is_assessor(request)

    def get_is_approver(self, obj):
        request = self.context["request"]
        return is_approver(request)

    def get_requirement_docs(self, obj):
        if obj.requirement_docs and obj.requirement_docs._file:
            return [[d.name, d._file.url] for d in obj.requirement_docs]
        return None

    def get_groups_comma_list(self, obj):
        return obj.current_proposal.groups_comma_list


class ApprovalExtendSerializer(serializers.Serializer):
    extend_details = serializers.CharField()


class ApprovalCancellationSerializer(serializers.Serializer):
    cancellation_date = serializers.DateField(input_formats=["%d/%m/%Y"])
    cancellation_details = serializers.CharField()


class ApprovalSuspensionSerializer(serializers.Serializer):
    from_date = serializers.DateField(input_formats=["%d/%m/%Y"])
    to_date = serializers.DateField(
        input_formats=["%d/%m/%Y"], required=False, allow_null=True
    )
    suspension_details = serializers.CharField()


class ApprovalSurrenderSerializer(serializers.Serializer):
    surrender_date = serializers.DateField(input_formats=["%d/%m/%Y"])
    surrender_details = serializers.CharField()


class ApprovalUserActionSerializer(serializers.ModelSerializer):
    who = serializers.CharField(source="who_full_name")

    class Meta:
        model = ApprovalUserAction
        fields = "__all__"


class ApprovalLogEntrySerializer(CommunicationLogEntrySerializer):
    class Meta:
        model = ApprovalLogEntry
        fields = "__all__"
        read_only_fields = ("customer",)


class ApprovalDocumentHistorySerializer(serializers.ModelSerializer):
    history_date = serializers.SerializerMethodField()
    history_document_url = serializers.SerializerMethodField()

    class Meta:
        model = ApprovalDocument
        fields = (
            "history_date",
            "history_document_url",
        )

    def get_history_date(self, obj):
        date_format_loc = timezone.localtime(obj.uploaded_date)
        history_date = date_format_loc.strftime("%d/%m/%Y %H:%M:%S.%f")

        return history_date

    def get_history_document_url(self, obj):
        # Todo: Change to secure file / document url
        url = obj._file.url
        return url
