from django.conf import settings
from django_countries.serializers import CountryFieldMixin
from ledger_api_client.ledger_models import Address
from ledger_api_client.ledger_models import EmailUserRO as EmailUser
from rest_framework import serializers

from leaseslicensing.components.compliances.models import ComplianceReferral
from leaseslicensing.components.main.models import (
    CommunicationsLogEntry,
    Document,
    UserSystemSettings,
)
from leaseslicensing.components.organisations.models import Organisation
from leaseslicensing.components.organisations.utils import can_admin_org, is_consultant
from leaseslicensing.components.proposals.models import ProposalApplicant, Referral
from leaseslicensing.components.users.models import EmailUserAction, EmailUserLogEntry
from leaseslicensing.helpers import (
    is_approver,
    is_assessor,
    is_internal,
    is_leaseslicensing_admin,
)


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ("id", "description", "file", "name", "uploaded_date")


class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ("id", "line1", "locality", "state", "country", "postcode")


class UserSystemSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSystemSettings
        fields = ("one_row_per_park",)


class UserOrganisationSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="organisation.name")
    abn = serializers.CharField(source="organisation.abn")
    email = serializers.SerializerMethodField()
    is_consultant = serializers.SerializerMethodField(read_only=True)
    is_admin = serializers.SerializerMethodField(read_only=True)
    active_proposals = serializers.SerializerMethodField(read_only=True)
    current_event_proposals = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Organisation
        fields = (
            "id",
            "name",
            "abn",
            "email",
            "is_consultant",
            "is_admin",
            "active_proposals",
            "current_event_proposals",
        )

    def get_is_admin(self, obj):
        user = EmailUser.objects.get(id=self.context.get("user_id"))
        return can_admin_org(obj, user)

    def get_is_consultant(self, obj):
        user = EmailUser.objects.get(id=self.context.get("user_id"))
        return is_consultant(obj, user)

    def get_email(self, obj):
        email = EmailUser.objects.get(id=self.context.get("user_id")).email
        return email


class UserFilterSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = EmailUser
        fields = ("id", "last_name", "first_name", "email", "name")

    def get_name(self, obj):
        return obj.get_full_name()


class UserSerializerSimple(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = EmailUser
        fields = ("id", "last_name", "first_name", "email", "full_name")

    def get_full_name(self, obj):
        return obj.get_full_name()


class ProposalApplicantSerializer(CountryFieldMixin, serializers.ModelSerializer):
    class Meta:
        model = ProposalApplicant
        fields = (
            "id",
            "last_name",
            "first_name",
            "dob",
            "residential_line1",
            "residential_line2",
            "residential_line3",
            "residential_locality",
            "residential_state",
            "residential_country",
            "residential_postcode",
            "postal_same_as_residential",
            "postal_line1",
            "postal_line2",
            "postal_line3",
            "postal_locality",
            "postal_state",
            "postal_country",
            "postal_postcode",
            "email",
            "phone_number",
            "mobile_number",
        )


class UserSerializer(serializers.ModelSerializer):
    residential_address = UserAddressSerializer()
    postal_address = UserAddressSerializer()
    personal_details = serializers.SerializerMethodField()
    address_details = serializers.SerializerMethodField()
    contact_details = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    is_internal = serializers.SerializerMethodField()
    is_leaseslicensing_admin = serializers.SerializerMethodField()
    is_assessor = serializers.SerializerMethodField()
    is_approver = serializers.SerializerMethodField()
    is_referee = serializers.SerializerMethodField()
    is_compliance_referee = serializers.SerializerMethodField()

    class Meta:
        model = EmailUser
        fields = (
            "id",
            "last_name",
            "first_name",
            "email",
            "residential_address",
            "postal_address",
            "phone_number",
            "mobile_number",
            "personal_details",
            "address_details",
            "contact_details",
            "full_name",
            "is_internal",
            "is_staff",
            "is_leaseslicensing_admin",
            "is_assessor",
            "is_approver",
            "is_referee",
            "is_compliance_referee",
        )

    def get_personal_details(self, obj):
        return True if obj.last_name and obj.first_name else False

    def get_address_details(self, obj):
        return True if obj.residential_address or obj.postal_address else False

    def get_contact_details(self, obj):
        if obj.mobile_number and obj.email:
            return True
        elif obj.phone_number and obj.email:
            return True
        elif obj.mobile_number and obj.phone_number:
            return True
        else:
            return False

    def get_full_name(self, obj):
        return obj.full_name if hasattr(obj, "full_name") else obj.get_full_name()

    def get_is_internal(self, obj):
        request = self.context["request"] if self.context else None
        if request:
            return is_internal(request)
        return False

    def get_is_assessor(self, obj):
        request = self.context["request"] if self.context else None
        if request:
            return is_assessor(request)
        return False

    def get_is_approver(self, obj):
        request = self.context["request"] if self.context else None
        if request:
            return is_approver(request)
        return False

    def get_is_leaseslicensing_admin(self, obj):
        request = self.context["request"] if self.context else None
        if request:
            return is_leaseslicensing_admin(request)
        return False

    def get_is_referee(self, obj):
        return Referral.objects.filter(
            referral=obj.id, processing_status=Referral.PROCESSING_STATUS_WITH_REFERRAL
        ).exists()

    def get_is_compliance_referee(self, obj):
        return ComplianceReferral.objects.filter(
            referral=obj.id,
            processing_status=ComplianceReferral.PROCESSING_STATUS_WITH_REFERRAL,
        ).exists()


class PersonalSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailUser
        fields = (
            "id",
            "last_name",
            "first_name",
        )


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailUser
        fields = (
            "id",
            "email",
            "phone_number",
            "mobile_number",
        )

    def validate(self, obj):
        # Mobile and phone number for dbca user are updated from active directory
        # so need to skip these users from validation.
        domain = None
        if obj["email"]:
            domain = obj["email"].split("@")[1]
        if domain in settings.DEPT_DOMAINS:
            return obj
        else:
            if not obj.get("phone_number") and not obj.get("mobile_number"):
                raise serializers.ValidationError(
                    "You must provide a mobile/phone number"
                )
        return obj


class EmailUserActionSerializer(serializers.ModelSerializer):
    who = serializers.CharField(source="who_full_name")

    class Meta:
        model = EmailUserAction
        fields = "__all__"


class EmailUserCommsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailUserLogEntry
        fields = "__all__"


class CommunicationLogEntrySerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(
        queryset=EmailUser.objects.all(), required=False
    )
    documents = serializers.SerializerMethodField()

    class Meta:
        model = CommunicationsLogEntry
        fields = (
            "id",
            "customer",
            "to",
            "fromm",
            "cc",
            "log_type",
            "reference",
            "subject" "text",
            "created",
            "staff",
            "emailuser",
            "documents",
        )

    def get_documents(self, obj):
        return [[d.name, d._file.url] for d in obj.documents.all()]


class EmailUserLogEntrySerializer(CommunicationLogEntrySerializer):
    class Meta:
        model = EmailUserLogEntry
        fields = "__all__"
        read_only_fields = (
            "customer",
            "documents",
        )
