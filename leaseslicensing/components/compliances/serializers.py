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
from leaseslicensing.components.main.utils import get_secure_document_url, get_secure_file_url
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
        return [
            get_secure_file_url(obj, "_file")
        ]


class ComplianceReferralDocumentSerializer(serializers.ModelSerializer):
    secure_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ComplianceReferralDocument
        fields = "__all__"

    def get_secure_url(self, obj):
        return [
            get_secure_file_url(obj, "_file")
        ]


class ComplianceReferralSerializer(serializers.ModelSerializer):
    referral_obj = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ComplianceReferral
        fields = "__all__"
        datatables_always_serialize = [
            "id",
        ]

    def get_referral_obj(self, obj):
        referral_email_user = retrieve_email_user(obj.referral)
        serializer = EmailUserSerializer(referral_email_user)
        return serializer.data


class ComplianceAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplianceAssessment
        fields = "__all__"


class ComplianceAmendmentRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = ComplianceAmendmentRequest
        fields = "__all__"


class BaseComplianceSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source="proposal.title")
    holder = serializers.CharField(read_only=True)
    processing_status = serializers.CharField(source="get_processing_status_display")
    customer_status = serializers.CharField(source="get_customer_status_display")
    submitter = serializers.SerializerMethodField(read_only=True)
    documents = ComplianceDocumentSerializer(many=True, read_only=True)
    allowed_assessors = serializers.SerializerMethodField(read_only=True)
    requirement = serializers.CharField(
        source="requirement.requirement", required=False, allow_null=True
    )
    approval_lodgement_number = serializers.SerializerMethodField()
    current_amendment_requests = ComplianceAmendmentRequestSerializer(many=True, read_only=True)
    assessment = ComplianceAssessmentSerializer(read_only=True)
    referrals = ComplianceReferralSerializer(many=True, read_only=True)

    class Meta:
        model = Compliance
        fields = [
            "id",
            "lodgement_number",
            "title",
            "text",
            "holder",
            "processing_status",
            "customer_status",
            "submitter",
            "documents",
            "allowed_assessors",
            "requirement",
            "approval_lodgement_number",
            "can_process",
            "can_user_view",
            "current_amendment_requests",
            "assessment",
            "referrals",
        ]
        datatables_always_serialize = [
            "id",
            "can_process",
            "can_user_view",
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


class ComplianceSerializer(BaseComplianceSerializer):
    application_type = serializers.SerializerMethodField(read_only=True)
    due_date = serializers.SerializerMethodField(read_only=True)
    lodgement_date_display = serializers.SerializerMethodField(read_only=True)
    assigned_to_name = serializers.CharField(read_only=True)

    class Meta:
        model = Compliance
        fields = BaseComplianceSerializer.Meta.fields + [
            "application_type",
            "due_date",
            "lodgement_date_display",
            "assigned_to_name",
        ]
        datatables_always_serialize = BaseComplianceSerializer.Meta.datatables_always_serialize

    def get_due_date(self, obj):
        return obj.due_date.strftime("%d/%m/%Y") if obj.due_date else ""

    def get_application_type(self, obj):
        if obj.proposal.application_type:
            return obj.proposal.application_type.name_display
        return None

    def get_lodgement_date_display(self, obj):
        if obj.lodgement_date:
            return (
                obj.lodgement_date.strftime("%d/%m/%Y")
                + " at "
                + obj.lodgement_date.strftime("%I:%M %p")
            )


class InternalComplianceSerializer(BaseComplianceSerializer):
    lodgement_date = serializers.SerializerMethodField()

    class Meta:
        model = Compliance
        fields = BaseComplianceSerializer.Meta.fields + [
            "approval",
            "reference",
            "assigned_to",
            "lodgement_date",
        ]
        datatables_always_serialize = BaseComplianceSerializer.Meta.datatables_always_serialize

    def get_lodgement_date(self, obj):
        return obj.lodgement_date.strftime("%d/%m/%Y") if obj.lodgement_date else ""


class SaveComplianceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compliance
        fields = (
            "id",
            "title",
            "text",
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
