import logging

from django.urls import reverse
from ledger_api_client.managed_models import SystemGroup
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from leaseslicensing.components.competitive_processes.models import (
    CompetitiveProcess,
    CompetitiveProcessAct,
    CompetitiveProcessCategory,
    CompetitiveProcessDistrict,
    CompetitiveProcessGeometry,
    CompetitiveProcessIdentifier,
    CompetitiveProcessLGA,
    CompetitiveProcessLogEntry,
    CompetitiveProcessName,
    CompetitiveProcessParty,
    CompetitiveProcessRegion,
    CompetitiveProcessTenure,
    CompetitiveProcessUserAction,
    CompetitiveProcessVesting,
    PartyDetail,
)
from leaseslicensing.components.main.models import upload_protected_files_storage
from leaseslicensing.components.main.serializers import (
    CommunicationLogEntrySerializer,
    EmailUserSerializer,
)
from leaseslicensing.components.main.utils import (
    get_polygon_source,
    get_secure_file_url,
)
from leaseslicensing.components.proposals.models import Proposal
from leaseslicensing.components.proposals.serializers import (
    ProposalGeometrySerializer,
    ProposalSerializer,
)
from leaseslicensing.components.tenure.models import Group
from leaseslicensing.components.tenure.serializers import GroupSerializer
from leaseslicensing.components.users.serializers import UserSerializerSimple
from leaseslicensing.ledger_api_utils import retrieve_email_user
from leaseslicensing.settings import GROUP_NAME_CHOICES

from ... import settings
from ..main.models import TemporaryDocumentCollection
from ..organisations.serializers import OrganisationSerializer

logger = logging.getLogger(__name__)


class RegistrationOfInterestSerializer(serializers.ModelSerializer):
    relevant_applicant_name = serializers.CharField()
    proposalgeometry = serializers.SerializerMethodField()
    application_type_name_display = serializers.CharField(
        read_only=True, source="application_type.name_display"
    )
    processing_status_display = serializers.CharField(
        read_only=True, source="get_processing_status_display"
    )
    lodgement_date_display = serializers.DateTimeField(
        read_only=True, format="%d/%m/%Y", source="lodgement_date"
    )
    details_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Proposal
        fields = (
            "id",
            "lodgement_number",
            "relevant_applicant_name",
            "proposalgeometry",
            "applicant_id",
            "processing_status",
            "application_type_name_display",
            "processing_status_display",
            "lodgement_date_display",
            "details_url",
        )

    def get_details_url(self, obj):
        return reverse("internal-proposal-detail", kwargs={"pk": obj.id})

    def get_proposalgeometry(self, obj):
        """
        Returns proposalgeometries for this Registration of Interest as FeatureCollection dict
        """

        geometry_data = {"type": "FeatureCollection", "features": []}
        for proposalgeometry in obj.proposalgeometry.all():
            pg_serializer = ProposalGeometrySerializer(proposalgeometry)
            geometry_data["features"].append(pg_serializer.data)

        return geometry_data


class PartyDetailSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField()
    temporary_document_collection_id = serializers.IntegerField(default=0)
    party_detail_documents = serializers.SerializerMethodField()

    class Meta:
        model = PartyDetail
        fields = (
            "id",
            "detail",
            "created_at",
            "modified_at",
            "created_by",
            "created_by_id",
            "temporary_document_collection_id",
            "party_detail_documents",
        )
        extra_kwargs = {
            "id": {
                "read_only": False,
                "required": False,
            },
            "party_detail_documents": {
                "read_only": True,
                "required": False,
            },
        }

    def get_party_detail_documents(self, obj):
        ret_array = []
        for item in obj.party_detail_documents.all():
            secure_url = get_secure_file_url(item, "_file")
            ret_array.append(
                {"name": item.name, "file": item._file.url, "secure_url": secure_url}
            )
        return ret_array

    def get_created_by(self, obj):
        serializer = EmailUserSerializer(obj.created_by)
        return serializer.data

    def update(self, instance, validated_data):
        # For now, we don't update this record once saved
        pass

    def create(self, validated_data):
        temporary_document_collection_id = validated_data.pop(
            "temporary_document_collection_id", 0
        )
        validated_data.pop(
            "id", 0
        )  # When create, we don't want to specify id.  That's why the 'id' is removed here.

        instance = PartyDetail.objects.create(**validated_data)

        if temporary_document_collection_id:
            if TemporaryDocumentCollection.objects.filter(
                id=temporary_document_collection_id
            ):
                temp_doc_collection = TemporaryDocumentCollection.objects.filter(
                    id=temporary_document_collection_id
                )[0]
                if temp_doc_collection:
                    for doc in temp_doc_collection.documents.all():
                        self.save_party_detail_document_obj(instance, doc)
                    temp_doc_collection.delete()
                    # instance.temporary_document_collection_id = None
                    # instance.save()

        return instance

    def save_party_detail_document_obj(self, instance, temp_document):
        new_document = instance.party_detail_documents.get_or_create(
            name=temp_document.name
        )[0]
        save_path = "{}/party_detail_document/{}/{}".format(
            settings.PROTECTED_MEDIA_ROOT,
            new_document.id,
            temp_document.name,
        )

        path = upload_protected_files_storage.save(save_path, temp_document._file)
        new_document._file = path
        new_document.save()


class CompetitiveProcessPartySerializer(serializers.ModelSerializer):
    is_person = serializers.BooleanField()  # This is property at the model
    is_organisation = serializers.BooleanField()  # This is property at the model
    person = serializers.SerializerMethodField()
    organisation = serializers.SerializerMethodField()
    organisation_id = serializers.IntegerField(allow_null=True, required=False)
    party_details = PartyDetailSerializer(many=True)

    class Meta:
        model = CompetitiveProcessParty
        fields = (
            "id",
            "is_person",
            "is_organisation",
            "person_id",
            "person",
            "organisation",
            "organisation_id",
            "invited_at",
            "removed_at",
            "created_at",
            "party_details",
            "email_address",
        )
        extra_kwargs = {
            "id": {
                "read_only": False,
                "required": False,
            },
        }

    def get_person(self, obj):
        if obj.is_person:
            serializer = EmailUserSerializer(obj.person)
            return serializer.data
        return None

    def get_organisation(self, obj):
        if obj.is_organisation:
            serializer = OrganisationSerializer(obj.organisation)
            return serializer.data
        return None

    def create(self, validated_data):
        validated_data.pop("id", None)  # Remove id not to update the object with id: 0
        validated_data.pop("is_person", None)
        validated_data.pop("is_organisation", None)
        party_details = validated_data.pop("party_details", None)

        instance = CompetitiveProcessParty.objects.create(**validated_data)
        self.handle_party_details(instance, party_details)

        return instance

    def update(self, instance, validated_data):
        instance.invited_at = validated_data.get("invited_at", None)
        instance.removed_at = validated_data.get("removed_at", None)
        instance.save()

        party_details = validated_data.get("party_details", None)
        self.handle_party_details(instance, party_details)

        return instance

    def handle_party_details(self, instance, party_details):
        self.context["competitive_process_party"] = instance
        for party_detail in party_details:
            if party_detail["id"]:
                # We don't update detail once saved
                pass
            else:
                # New competitive_process_party
                party_detail.pop(
                    "id", None
                )  # Otherwise update the object with this id, not creating new
                serializer = PartyDetailSerializer(
                    data=party_detail, context=self.context
                )
                serializer.is_valid(raise_exception=True)
                new_detail = serializer.save()
                new_detail.competitive_process_party = instance
                new_detail.save()


class CompetitiveProcessGeometrySaveSerializer(GeoFeatureModelSerializer):
    competitive_process_id = serializers.IntegerField(write_only=True, required=False)
    polygon_source = serializers.SerializerMethodField()

    class Meta:
        model = CompetitiveProcessGeometry
        geo_field = "polygon"
        fields = (
            "id",
            "competitive_process_id",
            "polygon",
            "intersects",
            "polygon_source",
            "drawn_by",
            "locked",
        )
        read_only_fields = ("id",)

    def get_polygon_source(self, obj):
        return get_polygon_source(obj)


class CompetitiveProcessIdentifierSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="identifier.id", read_only=True)
    name = serializers.CharField(source="identifier.name", read_only=True)

    class Meta:
        model = CompetitiveProcessIdentifier
        fields = ["id", "name"]


class CompetitiveProcessVestingSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="vesting.id", read_only=True)
    name = serializers.CharField(source="vesting.name", read_only=True)

    class Meta:
        model = CompetitiveProcessVesting
        fields = ["id", "name"]


class CompetitiveProcessNameSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="name.id", read_only=True)
    name = serializers.CharField(source="name.name", read_only=True)

    class Meta:
        model = CompetitiveProcessName
        fields = ["id", "name"]


class CompetitiveProcessActSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="act.id", read_only=True)
    name = serializers.CharField(source="act.name", read_only=True)

    class Meta:
        model = CompetitiveProcessAct
        fields = ["id", "name"]


class CompetitiveProcessTenureSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="tenure.id", read_only=True)
    name = serializers.CharField(source="tenure.name", read_only=True)

    class Meta:
        model = CompetitiveProcessTenure
        fields = ["id", "name"]


class CompetitiveProcessCategorySerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="category.id", read_only=True)
    name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = CompetitiveProcessCategory
        fields = ["id", "name"]


class CompetitiveProcessRegionSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="region.id", read_only=True)
    name = serializers.CharField(source="region.name", read_only=True)

    class Meta:
        model = CompetitiveProcessRegion
        fields = ["id", "name"]


class CompetitiveProcessDistrictSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="district.id", read_only=True)
    name = serializers.CharField(source="district.name", read_only=True)

    class Meta:
        model = CompetitiveProcessDistrict
        fields = ["id", "name"]


class CompetitiveProcessLGASerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="lga.id", read_only=True)
    name = serializers.CharField(source="lga.name", read_only=True)

    class Meta:
        model = CompetitiveProcessLGA
        fields = ["id", "name"]


class CompetititiveProcessGisDataSerializer(serializers.ModelSerializer):
    identifiers = CompetitiveProcessIdentifierSerializer(many=True, read_only=True)
    vestings = CompetitiveProcessVestingSerializer(many=True, read_only=True)
    names = CompetitiveProcessNameSerializer(many=True, read_only=True)
    acts = CompetitiveProcessActSerializer(many=True, read_only=True)
    tenures = CompetitiveProcessTenureSerializer(many=True, read_only=True)
    categories = CompetitiveProcessCategorySerializer(many=True, read_only=True)
    regions = CompetitiveProcessRegionSerializer(many=True, read_only=True)
    districts = CompetitiveProcessDistrictSerializer(many=True, read_only=True)
    lgas = CompetitiveProcessLGASerializer(many=True, read_only=True)

    class Meta:
        model = CompetitiveProcess
        fields = (
            "identifiers",
            "vestings",
            "names",
            "acts",
            "tenures",
            "categories",
            "regions",
            "districts",
            "lgas",
        )


class CompetitiveProcessSerializerBase(serializers.ModelSerializer):
    registration_of_interest = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    status_id = serializers.CharField(source="status", required=False)
    assigned_officer = serializers.SerializerMethodField()
    site_name = serializers.CharField(
        source="site_name.name", allow_null=True, read_only=True
    )
    groups = serializers.SerializerMethodField(read_only=True)
    can_accessing_user_view = serializers.SerializerMethodField()
    can_accessing_user_process = serializers.SerializerMethodField()
    details_url = serializers.SerializerMethodField(read_only=True)

    # Gis data fields
    gis_data = serializers.SerializerMethodField()

    class Meta:
        model = CompetitiveProcess
        fields = (
            "id",
            "lodgement_number",
            "registration_of_interest",
            "generated_proposal",
            "status",
            "created_at",
            "assigned_officer",
            "site_name",
            "site_comments",
            "groups",
            "can_accessing_user_view",
            "can_accessing_user_process",
            "details_url",
            "gis_data",
        )
        # additional data to be returned for datatable
        # fields listed here should be listed 'fields' above, otherwise not returned
        datatables_always_serialize = (
            "registration_of_interest",
            "created_at",
            "groups",
            "site_name",
            "can_accessing_user_view",
            "can_accessing_user_process",
        )

    def get_groups(self, obj):
        group_ids = obj.groups.values_list("group__id", flat=True)
        group_qs = Group.objects.filter(id__in=group_ids).values("id", "name")
        return GroupSerializer(group_qs, many=True).data

    def get_details_url(self, obj):
        return reverse("internal-competitiveprocess-detail", kwargs={"pk": obj.id})

    def get_registration_of_interest(self, obj):
        if obj.generated_from_registration_of_interest:
            return RegistrationOfInterestSerializer(obj.originating_proposal).data
        else:
            return None

    def get_status(self, obj):
        return (
            obj.get_status_display()
        )  # https://docs.djangoproject.com/en/3.2/ref/models/instances/#django.db.models.Model.get_FOO_display
        # return {'key': obj.status, 'text': obj.get_status_display()}

    def get_assigned_officer(self, obj):
        if obj.is_assigned:
            return EmailUserSerializer(obj.assigned_officer).data
        else:
            return None

    def get_can_accessing_user_view(self, obj):
        request = self.context.get("request")
        can_view = obj.can_user_view(request)
        return can_view

    def get_can_accessing_user_process(self, obj):
        user = self.context.get("request").user
        can_process = obj.can_user_process(user)
        return can_process

    def get_gis_data(self, obj):
        return CompetititiveProcessGisDataSerializer(obj).data


class ListCompetitiveProcessSerializer(CompetitiveProcessSerializerBase):
    class Meta:
        model = CompetitiveProcess
        fields = (
            "id",
            "lodgement_number",
            "registration_of_interest",
            "status",
            "created_at",
            "assigned_officer",
            "site_name",
            "groups",
            "can_accessing_user_view",
            "can_accessing_user_process",
        )
        # additional data to be returned for datatable
        # fields listed here should be listed 'fields' above, otherwise not returned
        datatables_always_serialize = (
            "id",
            "lodgement_number",
            "registration_of_interest",
            "created_at",
            "site_name",
            "groups",
            "can_accessing_user_view",
            "can_accessing_user_process",
        )


class CompetitiveProcessSerializer(CompetitiveProcessSerializerBase):
    model_name = serializers.CharField(read_only=True)
    accessing_user = serializers.SerializerMethodField()
    competitive_process_parties = CompetitiveProcessPartySerializer(
        many=True, required=False
    )
    competitive_process_geometries = CompetitiveProcessGeometrySaveSerializer(
        many=True, read_only=True
    )
    allowed_editors = serializers.SerializerMethodField(read_only=True)
    accessing_user_roles = serializers.SerializerMethodField()
    accessing_user_is_competitive_process_editor = serializers.SerializerMethodField()
    generated_proposal = ProposalSerializer(many=True, required=False, read_only=True)
    winner = CompetitiveProcessPartySerializer(allow_null=True, required=False)
    label = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CompetitiveProcess
        fields = (
            "id",
            "model_name",
            "lodgement_number",
            "registration_of_interest",
            "generated_proposal",
            "status",
            "status_id",
            "created_at",
            "assigned_officer",
            "site_name",
            "site_comments",
            "groups",
            "gis_data",
            "can_accessing_user_view",
            "can_accessing_user_process",
            "accessing_user_is_competitive_process_editor",
            "accessing_user",
            "competitive_process_parties",
            "winner",
            "winner_id",
            "details",
            "competitive_process_geometries",
            "allowed_editors",
            "accessing_user_roles",
            "label",  # A static value to be used on the map
            "details_url",
        )
        extra_kwargs = {
            "winner_id": {
                "read_only": False,
                "required": False,
            },
        }

    def get_label(self, obj):
        return "Competitive Process"

    def get_accessing_user(self, obj):
        user = self.context.get("request").user
        serializer = UserSerializerSimple(user)
        return serializer.data

    def get_accessing_user_is_competitive_process_editor(self, obj):
        request = self.context.get("request")
        return obj.is_user_competitive_process_editor(request.user.id)

    def get_accessing_user_roles(self, obj):
        request = self.context.get("request")
        accessing_user = request.user
        roles = []

        for choice in GROUP_NAME_CHOICES:
            group = SystemGroup.objects.get(name=choice[0])
            ids = group.get_system_group_member_ids()
            if accessing_user.id in ids:
                roles.append(group.name)

        return roles

    def update(self, instance, validated_data):
        competitive_process_parties_data = validated_data.pop(
            "competitive_process_parties"
        )

        winner = validated_data.pop("winner", None)
        if winner and isinstance(winner, dict):
            instance.winner = CompetitiveProcessParty.objects.get(pk=winner["id"])
        else:
            instance.winner = winner

        instance.details = validated_data["details"]
        instance.save()

        super().update(instance, validated_data)

        # competitive_process_parties
        for competitive_process_party_data in competitive_process_parties_data:
            # Existing competitive process parties have a positive id
            if competitive_process_party_data["id"] > 0:
                # This competitive_process_party exists
                competitive_process_party_instance = (
                    CompetitiveProcessParty.objects.get(
                        id=int(competitive_process_party_data["id"])
                    )
                )
                serializer = CompetitiveProcessPartySerializer(
                    competitive_process_party_instance,
                    competitive_process_party_data,
                    context={"competitive_process": instance},
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()
            else:
                # New competitive_process_party has a negative id (set in the frontend)
                serializer = CompetitiveProcessPartySerializer(
                    data=competitive_process_party_data,
                    context={"competitive_process": instance},
                )
                serializer.is_valid(raise_exception=True)
                new_party = serializer.save()
                new_party.competitive_process = instance
                new_party.save()

        return instance

    def get_allowed_editors(self, obj):
        if obj.allowed_editors:
            email_users = []
            for user in obj.allowed_editors:
                email_users.append(user)
            return EmailUserSerializer(email_users, many=True).data
        else:
            return ""


class CompetitiveProcessLogEntrySerializer(CommunicationLogEntrySerializer):
    class Meta:
        model = CompetitiveProcessLogEntry
        fields = "__all__"
        read_only_fields = ("customer",)


class CompetitiveProcessUserActionSerializer(serializers.ModelSerializer):
    who = serializers.SerializerMethodField()

    class Meta:
        model = CompetitiveProcessUserAction
        fields = "__all__"

    def get_who(self, proposal_user_action):
        email_user = retrieve_email_user(proposal_user_action.who)
        fullname = email_user.get_full_name()
        return fullname


class CompetitiveProcessMapFeatureInfoSerializer(CompetitiveProcessSerializer):
    created_at_display = serializers.DateTimeField(
        read_only=True, format="%d/%m/%Y", source="created_at"
    )
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = CompetitiveProcess
        fields = (
            "id",
            "label",  # application_type_name_display
            "details_url",
            "lodgement_number",
            "created_at_display",  # lodgement_date_display @proposal
            "status_display",  # processing_status_display"
        )

    def get_status_display(self, obj):
        return {i[0]: i[1] for i in CompetitiveProcess.STATUS_CHOICES}.get(
            obj.status, None
        )
