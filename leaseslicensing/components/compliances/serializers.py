from rest_framework import serializers

from leaseslicensing.components.compliances.models import (
    Compliance,
    ComplianceAmendmentRequest,
    ComplianceAssessment,
    ComplianceDocument,
    ComplianceLogEntry,
    ComplianceReferral,
    ComplianceReferralDocument,
    ComplianceUserAction,
)
from leaseslicensing.components.main.serializers import EmailUserSerializer
from leaseslicensing.components.main.utils import get_secure_file_url
from leaseslicensing.ledger_api_utils import retrieve_email_user


class ComplianceDocumentSerializer(serializers.ModelSerializer):
    secure_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ComplianceDocument
        fields = (
            "name",
            "_file",
            "secure_url",
            "can_delete",
            "id",
        )

    def get_secure_url(self, obj):
        return [get_secure_file_url(obj, "_file")]


class ComplianceReferralDocumentSerializer(serializers.ModelSerializer):
    secure_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ComplianceReferralDocument
        fields = "__all__"

    def get_secure_url(self, obj):
        return [get_secure_file_url(obj, "_file")]


class UpdateComplianceReferralSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplianceReferral
        fields = [
            "comment",
        ]


class ComplianceReferralSerializer(serializers.ModelSerializer):
    referee_obj = serializers.SerializerMethodField(read_only=True)
    processing_status_display = serializers.CharField(
        source="get_processing_status_display", read_only=True
    )

    class Meta:
        model = ComplianceReferral
        fields = "__all__"
        datatables_always_serialize = [
            "id",
        ]

    def get_referee_obj(self, obj):
        return EmailUserSerializer(retrieve_email_user(obj.referral)).data


class ComplianceReferralDatatableSerializer(serializers.ModelSerializer):
    # Have to use the same field names as the serializer used for datatables in the proposals component
    referral = serializers.SerializerMethodField(read_only=True)
    referral_status = serializers.CharField(
        source="get_processing_status_display", read_only=True
    )

    class Meta:
        model = ComplianceReferral
        fields = "__all__"
        datatables_always_serialize = [
            "id",
        ]

    def get_referral(self, obj):
        return EmailUserSerializer(retrieve_email_user(obj.referral)).data


class UpdateComplianceAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplianceAssessment
        fields = [
            "assessor_comment",
            "deficiency_comment",
        ]


class ComplianceAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplianceAssessment
        fields = "__all__"


class ComplianceAmendmentRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplianceAmendmentRequest
        fields = "__all__"


class BaseComplianceSerializer(serializers.ModelSerializer):
    approval_type = serializers.CharField(
        source="approval.approval_type.name", read_only=True
    )
    title = serializers.CharField(source="proposal.title", read_only=True)
    holder = serializers.CharField(read_only=True)
    processing_status_display = serializers.CharField(
        source="get_processing_status_display", read_only=True
    )
    customer_status_display = serializers.CharField(
        source="get_customer_status_display", read_only=True
    )
    submitter = serializers.SerializerMethodField(read_only=True)
    documents = ComplianceDocumentSerializer(many=True, read_only=True)
    allowed_assessors = serializers.SerializerMethodField(read_only=True)
    requirement = serializers.CharField(
        source="requirement.requirement",
        required=False,
        allow_null=True,
        read_only=True,
    )
    approval_lodgement_number = serializers.SerializerMethodField()
    current_amendment_requests = ComplianceAmendmentRequestSerializer(
        many=True, read_only=True
    )
    assessment = ComplianceAssessmentSerializer(read_only=True)
    referrals = ComplianceReferralSerializer(many=True, read_only=True)
    latest_referrals = ComplianceReferralSerializer(many=True, read_only=True)
    is_referee = serializers.SerializerMethodField(read_only=True)
    gross_turnover_required = serializers.BooleanField(read_only=True)
    gross_turnover = serializers.DecimalField(
        allow_null=True, max_digits=15, decimal_places=2
    )

    class Meta:
        model = Compliance
        fields = [
            "id",
            "lodgement_number",
            "title",
            "text",
            "holder",
            "processing_status",
            "processing_status_display",
            "customer_status",
            "customer_status_display",
            "submitter",
            "documents",
            "allowed_assessors",
            "requirement",
            "approval_lodgement_number",
            "can_process",
            "can_user_view",
            "is_referee",
            "current_amendment_requests",
            "assessment",
            "referrals",
            "latest_referrals",
            "approval_type",
            "gross_turnover_required",
            "gross_turnover",
        ]
        datatables_always_serialize = [
            "id",
            "processing_status_display",
            "customer_status_display",
            "can_process",
            "can_user_view",
            "is_referee",
        ]

    def get_submitter(self, obj):
        if obj.submitter:
            return retrieve_email_user(obj.submitter).get_full_name()
        return None

    def get_allowed_assessors(self, obj):
        if obj.allowed_assessors:
            email_users = []
            for user in obj.allowed_assessors:
                email_users.append(retrieve_email_user(user))
            return EmailUserSerializer(email_users, many=True).data
        else:
            return ""

    def get_approval_lodgement_number(self, obj):
        return obj.approval.lodgement_number

    def get_is_referee(self, obj):
        request = self.context["request"]
        return obj.is_referee(request.user.id)


class ComplianceSerializer(BaseComplianceSerializer):
    due_date = serializers.SerializerMethodField(read_only=True)
    lodgement_date_display = serializers.SerializerMethodField(read_only=True)
    assigned_to_name = serializers.CharField(read_only=True)
    referral_processing_status = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Compliance
        fields = BaseComplianceSerializer.Meta.fields + [
            "due_date",
            "lodgement_date_display",
            "assigned_to_name",
            "referral_processing_status",
        ]
        datatables_always_serialize = (
            BaseComplianceSerializer.Meta.datatables_always_serialize
            + ["referral_processing_status"]
        )

    def get_due_date(self, obj):
        return obj.due_date.strftime("%d/%m/%Y") if obj.due_date else ""

    def get_lodgement_date_display(self, obj):
        if obj.lodgement_date:
            return (
                obj.lodgement_date.strftime("%d/%m/%Y")
                + " at "
                + obj.lodgement_date.strftime("%I:%M %p")
            )

    def get_referral_processing_status(self, obj):
        if hasattr(obj, "referral_processing_status"):
            return obj.referral_processing_status
        return None


class InternalComplianceSerializer(BaseComplianceSerializer):
    lodgement_date = serializers.SerializerMethodField()
    # Only needed to match proposal field name so workflow_function.js can be used for both proposal and compliance
    processing_status_id = serializers.CharField(
        source="processing_status", read_only=True
    )

    class Meta:
        model = Compliance
        fields = BaseComplianceSerializer.Meta.fields + [
            "approval",
            "due_date",
            "reference",
            "assigned_to",
            "lodgement_date",
            "processing_status_id",
        ]
        datatables_always_serialize = (
            BaseComplianceSerializer.Meta.datatables_always_serialize
        )

    def get_lodgement_date(self, obj):
        return obj.lodgement_date.strftime("%d/%m/%Y") if obj.lodgement_date else ""


class SaveComplianceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compliance
        fields = (
            "id",
            "title",
            "text",
            "gross_turnover",
            "num_participants",
        )


class AssessorSaveComplianceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compliance
        fields = (
            "id",
            "title",
            "text",
            "gross_turnover",
            "num_participants",
        )


class ComplianceActionSerializer(serializers.ModelSerializer):
    who = serializers.CharField(source="who_full_name")

    class Meta:
        model = ComplianceUserAction
        fields = "__all__"


class ComplianceCommsSerializer(serializers.ModelSerializer):
    documents = serializers.SerializerMethodField()

    class Meta:
        model = ComplianceLogEntry
        fields = "__all__"

    def get_documents(self, obj):
        return [[d.name, d._file.url] for d in obj.documents.all()]


class CompAmendmentRequestDisplaySerializer(serializers.ModelSerializer):
    reason = serializers.SerializerMethodField()

    class Meta:
        model = ComplianceAmendmentRequest
        fields = "__all__"

    def get_reason(self, obj):
        return obj.reason.reason if obj.reason else None
