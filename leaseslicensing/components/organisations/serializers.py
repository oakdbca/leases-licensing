from django.conf import settings
from ledger_api_client.ledger_models import EmailUserRO as EmailUser
from rest_framework import serializers

from leaseslicensing.components.main.serializers import CommunicationLogEntrySerializer
from leaseslicensing.components.organisations.models import (
    Organisation,
    OrganisationAction,
    OrganisationContact,
    OrganisationLogEntry,
    OrganisationRequest,
    OrganisationRequestLogEntry,
    OrganisationRequestUserAction,
)
from leaseslicensing.components.organisations.utils import (
    can_admin_org,
    can_approve,
    can_manage_org,
    can_relink,
    is_consultant,
)
from leaseslicensing.components.users.serializers import ContactSerializer
from leaseslicensing.ledger_api_utils import retrieve_email_user


class OrganisationCheckSerializer(serializers.Serializer):
    # Validation serializer for new Organisations
    abn = serializers.CharField()
    name = serializers.CharField()

    def validate(self, data):
        # Check no admin request pending approval.
        requests = OrganisationRequest.objects.filter(
            abn=data["abn"], role="employee"
        ).exclude(status__in=("declined", "approved"))
        if requests.exists():
            raise serializers.ValidationError(
                "A request has been submitted and is Pending Approval."
            )
        return data


class OrganisationPinCheckSerializer(serializers.Serializer):
    pin1 = serializers.CharField()
    pin2 = serializers.CharField()


# class OrganisationAddressSerializer(serializers.ModelSerializer):
#    class Meta:
#        model = OrganisationAddress
#        fields = (
#            'id',
#            'line1',
#            'locality',
#            'state',
#            'country',
#            'postcode'
#        )


class DelegateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="get_full_name")

    class Meta:
        model = EmailUser
        fields = (
            "id",
            "name",
            "email",
        )


class OrganisationContactSerializer(serializers.ModelSerializer):
    user_status = serializers.SerializerMethodField()
    user_role = serializers.SerializerMethodField()

    class Meta:
        model = OrganisationContact
        fields = "__all__"

    def get_user_status(self, obj):
        return obj.get_user_status_display()

    def get_user_role(self, obj):
        return obj.get_user_role_display()


class OrganisationSerializer(serializers.ModelSerializer):
    # address = OrganisationAddressSerializer(read_only=True)
    pins = serializers.SerializerMethodField(read_only=True)
    # delegates = DelegateSerializer(many=True, read_only=True)
    delegate_organisation_contacts = serializers.ListField(
        child=OrganisationContactSerializer(), read_only=True
    )
    trading_name = serializers.CharField(source="organisation_name", read_only=True)
    apply_application_discount = serializers.SerializerMethodField(read_only=True)
    application_discount = serializers.SerializerMethodField(read_only=True)
    apply_licence_discount = serializers.SerializerMethodField(read_only=True)
    licence_discount = serializers.SerializerMethodField(read_only=True)
    charge_once_per_year = serializers.DateField(
        format="%d/%m", input_formats=["%d/%m"], required=False, allow_null=True
    )
    last_event_application_fee_date = serializers.DateField(
        format="%d/%m/%Y", input_formats=["%d/%m/%Y"], required=False, allow_null=True
    )

    class Meta:
        model = Organisation
        fields = (
            "id",
            "organisation",
            "organisation_abn",
            "organisation_email",
            "trading_name",
            "abn",
            "phone_number",
            "pins",
            "delegate_organisation_contacts",
            "apply_application_discount",
            "application_discount",
            "apply_licence_discount",
            "licence_discount",
            "charge_once_per_year",
            "max_num_months_ahead",
            "last_event_application_fee_date",
        )

    def get_apply_application_discount(self, obj):
        return obj.apply_application_discount

    def get_application_discount(self, obj):
        return obj.application_discount

    def get_apply_licence_discount(self, obj):
        return obj.apply_licence_discount

    def get_licence_discount(self, obj):
        return obj.licence_discount

    def get_charge_once_per_year(self, obj):
        return obj.charge_once_per_year

    def get_delegates(self, obj):
        """
        Default DelegateSerializer does not include whether the user is an organisation admin, so adding it here
        """
        delegates = []
        for user in obj.delegates.all():
            admin_qs = obj.contacts.filter(
                organisation__organisation_id=obj.organisation_id,
                email=user.email,
                is_admin=True,
                user_role="organisation_admin",
            )  # .values_list('is_admin',flat=True)
            if admin_qs.count() > 0:
                delegates.append(
                    dict(
                        id=user.id,
                        name=user.get_full_name(),
                        email=user.email,
                        is_admin=True,
                    )
                )
            else:
                delegates.append(
                    dict(
                        id=user.id,
                        name=user.get_full_name(),
                        email=user.email,
                        is_admin=False,
                    )
                )

        return delegates

    # def get_email(self, obj):
    #     return obj.ledger_organisation["email"]

    def get_trading_name(self, obj):
        return obj.ledger_organisation["organisation_name"]

    def get_pins(self, obj):
        try:
            user = self.context["request"].user
            # Check if the request user is among the first five delegates in the organisation
            if can_manage_org(obj, user):
                return {
                    "one": obj.admin_pin_one,
                    "two": obj.admin_pin_two,
                    "three": obj.user_pin_one,
                    "four": obj.user_pin_two,
                }
            else:
                return None
        except KeyError:
            return None


class OrganisationKeyValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organisation
        fields = ["id", "organisation_name"]
        read_only_fields = ["id", "organisation_name"]


class OrganisationCheckExistSerializer(serializers.Serializer):
    # Validation Serializer for existing Organisations
    exists = serializers.BooleanField(default=False)
    id = serializers.IntegerField(default=0)
    first_five = serializers.CharField(allow_blank=True, required=False)
    user = serializers.IntegerField()
    abn = serializers.CharField()

    def validate(self, data):
        user = EmailUser.objects.get(id=data["user"])
        if data["exists"]:
            org = Organisation.objects.get(id=data["id"])
            if can_relink(org, user):
                raise serializers.ValidationError(
                    "Please contact {} to re-link to Organisation.".format(
                        data["first_five"]
                    )
                )
            if can_approve(org, user):
                raise serializers.ValidationError(
                    "Please contact {} to Approve your request.".format(
                        data["first_five"]
                    )
                )
        # Check no consultant request is pending approval for an ABN
        if (
            OrganisationRequest.objects.filter(
                abn=data["abn"], requester=user, role="consultant"
            )
            .exclude(status__in=("declined", "approved"))
            .exists()
        ):
            raise serializers.ValidationError(
                "A request has been submitted and is Pending Approval."
            )
        return data


class MyOrganisationsSerializer(serializers.ModelSerializer):
    is_admin = serializers.SerializerMethodField(read_only=True)
    is_consultant = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Organisation
        fields = ("id", "name", "abn", "is_admin", "is_consultant")

    def get_is_consultant(self, obj):
        user = self.context["request"].user
        # Check if the request user is among the first five delegates in the organisation
        return is_consultant(obj, user)

    def get_is_admin(self, obj):
        user = self.context["request"].user
        # Check if the request user is among the first five delegates in the organisation
        return can_admin_org(obj, user)


class SaveDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organisation
        fields = (
            "id",
            "apply_application_discount",
            "application_discount",
            "apply_licence_discount",
            "licence_discount",
            "charge_once_per_year",
            "max_num_months_ahead",
        )


class OrgRequestRequesterSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = EmailUser
        fields = ("email", "mobile_number", "phone_number", "full_name")

    def get_full_name(self, obj):
        return obj.get_full_name()


class OrganisationRequestSerializer(serializers.ModelSerializer):
    identification = serializers.FileField()
    requester_name = serializers.SerializerMethodField(read_only=True)
    lodgement_date = serializers.DateTimeField(format="%d/%m/%Y")
    status = serializers.SerializerMethodField()
    ledger_organisation_name = serializers.SerializerMethodField()
    assigned_officer_name = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    class Meta:
        model = OrganisationRequest
        fields = "__all__"
        read_only_fields = (
            "requester",
            "requester_name",
            "lodgement_date",
            "assigned_officer",
        )

    def get_role(self, obj):
        return obj.get_role_display()

    def get_requester_name(self, obj):
        email_user = EmailUser.objects.filter(id=obj.requester).first()
        if email_user:
            return email_user.get_full_name()
        return None

    def get_status(self, obj):
        return obj.get_status_display()

    def get_ledger_organisation_name(self, obj):
        return obj.organisation.ledger_organisation["organisation_name"]

    def get_assigned_officer_name(self, obj):
        email_user = EmailUser.objects.filter(id=obj.assigned_officer).first()
        if email_user:
            return email_user.get_full_name()
        return None


class OrganisationRequestDTSerializer(OrganisationRequestSerializer):
    requester = serializers.SerializerMethodField()

    def get_requester(self, obj):
        email_user = retrieve_email_user(obj.requester)
        if email_user:
            return ContactSerializer(email_user).data
        return None


class UserOrganisationSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="organisation.name")
    abn = serializers.CharField(source="organisation.abn")

    class Meta:
        model = Organisation
        fields = ("id", "name", "abn")


class OrganisationRequestActionSerializer(serializers.ModelSerializer):
    who = serializers.SerializerMethodField()

    class Meta:
        model = OrganisationRequestUserAction
        fields = "__all__"

    def get_who(self, obj):
        email_user = EmailUser.objects.filter(id=obj.who).first()
        if email_user:
            return email_user.get_full_name()
        return None


class OrganisationActionSerializer(serializers.ModelSerializer):
    who = serializers.CharField(source="who_full_name")

    class Meta:
        model = OrganisationAction
        fields = "__all__"


class OrganisationRequestCommsSerializer(serializers.ModelSerializer):
    documents = serializers.SerializerMethodField()

    class Meta:
        model = OrganisationRequestLogEntry
        fields = "__all__"

    def get_documents(self, obj):
        return [[d.name, d._file.url] for d in obj.documents.all()]


class OrganisationCommsSerializer(serializers.ModelSerializer):
    documents = serializers.SerializerMethodField()

    class Meta:
        model = OrganisationLogEntry
        fields = "__all__"

    def get_documents(self, obj):
        return [[d.name, d._file.url] for d in obj.documents.all()]


class OrganisationRequestLogEntrySerializer(CommunicationLogEntrySerializer):
    documents = serializers.SerializerMethodField()

    class Meta:
        model = OrganisationRequestLogEntry
        fields = "__all__"
        read_only_fields = ("customer",)

    def get_documents(self, obj):
        return [[d.name, d._file.url] for d in obj.documents.all()]


class OrganisationLogEntrySerializer(CommunicationLogEntrySerializer):
    documents = serializers.SerializerMethodField()

    class Meta:
        model = OrganisationLogEntry
        fields = "__all__"
        read_only_fields = ("customer",)

    def get_documents(self, obj):
        return [[d.name, d._file.url] for d in obj.documents.all()]


class OrganisationUnlinkUserSerializer(serializers.Serializer):
    user = serializers.IntegerField()

    def validate(self, obj):
        user = None
        try:
            user = EmailUser.objects.get(id=obj["user"])
            obj["user_obj"] = user
        except EmailUser.DoesNotExist:
            raise serializers.ValidationError(
                "The user you want to unlink does not exist."
            )
        return obj


class OrgUserAcceptSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    mobile_number = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )
    phone_number = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )

    def validate(self, data):
        # Mobile and phone number for dbca user are updated from active directory
        # so need to skip these users from validation.
        domain = None
        if data["email"]:
            domain = data["email"].split("@")[1]
        if domain in settings.DEPT_DOMAINS:
            return data
        else:
            if not (data["mobile_number"] or data["phone_number"]):
                raise serializers.ValidationError(
                    "User must have an associated phone number or mobile number."
                )
        return data
