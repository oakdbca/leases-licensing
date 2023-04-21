from ledger_api_client.ledger_models import EmailUserRO
from ledger_api_client.ledger_models import EmailUserRO as EmailUser
from rest_framework import serializers

from leaseslicensing.components.main.models import (
    ApplicationType,
    CommunicationsLogEntry,
    GlobalSettings,
    MapColumn,
    MapLayer,
    Question,
    RequiredDocument,
    TemporaryDocumentCollection,
)

# from leaseslicensing.components.proposals.serializers import ProposalTypeSerializer


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
            "type",
            "reference",
            "subject" "text",
            "created",
            "staff",
            "proposal",
            "documents",
        )

    def get_documents(self, obj):
        return [[d.name, d._file.url] for d in obj.documents.all()]


class ApplicationTypeSerializer(serializers.ModelSerializer):
    name_display = serializers.CharField()
    confirmation_text = serializers.CharField()

    class Meta:
        model = ApplicationType
        fields = "__all__"
        read_only_fields = ["name_display", "confirmation_text"]


class ApplicationTypeKeyValueSerializer(serializers.ModelSerializer):
    name_display = serializers.SerializerMethodField()

    class Meta:
        model = ApplicationType
        fields = ["id", "name_display"]
        read_only_fields = ["id", "name_display"]

    def get_name_display(self, obj):
        return obj.get_name_display()


class GlobalSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalSettings
        fields = ("key", "value")


class RequiredDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequiredDocument
        fields = ("id", "park", "activity", "question")


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = (
            "id",
            "question_text",
            "answer_one",
            "answer_two",
            "answer_three",
            "answer_four",
            "correct_answer",
            "correct_answer_value",
        )


class BookingSettlementReportSerializer(serializers.Serializer):
    date = serializers.DateTimeField(input_formats=["%d/%m/%Y"])


class OracleSerializer(serializers.Serializer):
    date = serializers.DateField(input_formats=["%d/%m/%Y", "%Y-%m-%d"])
    override = serializers.BooleanField(default=False)


class MapColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = MapColumn
        fields = (
            "name",
            "option_for_internal",
            "option_for_external",
        )


class MapLayerSerializer(serializers.ModelSerializer):
    layer_full_name = serializers.SerializerMethodField()
    layer_group_name = serializers.SerializerMethodField()
    layer_name = serializers.SerializerMethodField()
    columns = MapColumnSerializer(many=True)

    class Meta:
        model = MapLayer
        fields = (
            "id",
            "display_name",
            "layer_full_name",
            "layer_group_name",
            "layer_name",
            "display_all_columns",
            "columns",
            "transparency",
        )
        read_only_fields = ("id",)

    def get_layer_full_name(self, obj):
        return obj.layer_name.strip()

    def get_layer_group_name(self, obj):
        return obj.layer_name.strip().split(":")[0]

    def get_layer_name(self, obj):
        return obj.layer_name.strip().split(":")[1]


class EmailUserROSerializerForReferral(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    telephone = serializers.CharField(source="phone_number")
    mobile_phone = serializers.CharField(source="mobile_number")

    class Meta:
        model = EmailUserRO
        fields = (
            "id",
            "name",
            "title",
            "email",
            "telephone",
            "mobile_phone",
        )

    def get_name(self, user):
        return user.get_full_name()


class EmailUserSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = EmailUser
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "title",
            "organisation",
            "fullname",
            "phone_number",
            "mobile_number"
        )

    def get_fullname(self, obj):
        return f"{obj.first_name} {obj.last_name}"



class TemporaryDocumentCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemporaryDocumentCollection
        fields = ("id",)
