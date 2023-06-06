from django.conf import settings
from django.urls import reverse
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
from leaseslicensing.components.main.utils import get_secure_document_url
from leaseslicensing.helpers import get_model_by_lodgement_number


class CommunicationLogEntrySerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(
        queryset=EmailUser.objects.all(), required=False
    )
    documents = serializers.SerializerMethodField()
    document_urls = serializers.SerializerMethodField()

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
            "document_urls",
        )
        datatables_always_serialize = ("documents", "document_urls")

    def get_documents(self, obj):
        return [[d.name] for d in obj.documents.all()]

    def get_document_urls(self, obj):
        return [
            get_secure_document_url(obj, "documents", d.id) for d in obj.documents.all()
        ]


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
            "mobile_number",
        )

    def get_fullname(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class TemporaryDocumentCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemporaryDocumentCollection
        fields = ("id",)


class SecureDocumentSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    description = serializers.CharField()
    name = serializers.CharField(read_only=True)
    uploaded_date = serializers.DateTimeField(read_only=True)
    url = serializers.SerializerMethodField()
    hyperlink = serializers.SerializerMethodField()
    model = None
    instance_id = None
    related_name = None

    def __init__(self, instance=None, data=..., **kwargs):
        model, instance_id, related_name = (
            kwargs.pop("model"),
            kwargs.pop("instance_id"),
            kwargs.pop("related_name"),
        )
        if not model or not instance_id or not related_name:
            raise ValueError(
                "model, instance_id and related_name are required to build a secure document url"
            )
        self.model = model
        self.instance_id = instance_id
        self.related_name = related_name
        super().__init__(instance, data, **kwargs)

    def get_url(self, obj):
        return f"{settings.SECURE_DOCUMENT_API_BASE_PATH}{self.model}/{self.instance_id}/{self.related_name}/{obj.id}/"

    def get_hyperlink(self, obj):
        return f"<a href='{self.get_url(obj)}'>{obj.name}</a>"


class RelatedItemSerializer(serializers.Serializer):
    """Generic related item serializer that uses object introspection to be able to show basic details
    for proposals, compliances and approvals all in the same result set"""

    id = serializers.IntegerField()
    lodgement_number = serializers.CharField()
    item_type = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    detail_url = serializers.SerializerMethodField()

    def get_item_type(self, obj):
        model = get_model_by_lodgement_number(obj["lodgement_number"])
        return model._meta.verbose_name.title()

    def get_description(self, obj):
        model = get_model_by_lodgement_number(obj["lodgement_number"])
        processing_status = obj["processing_status"]
        # Would be nice to have all the models use the same status field name in future
        if hasattr(model, "STATUS_CHOICES"):
            processing_status = dict(model.STATUS_CHOICES)[processing_status]
        elif hasattr(model, "PROCESSING_STATUS_CHOICES"):
            processing_status = dict(model.PROCESSING_STATUS_CHOICES)[processing_status]
        else:
            raise AttributeError(
                f"Model {model} does not have a STATUS_CHOICES or PROCESSING_STATUS_CHOICES attribute"
            )
        return f"Status: {processing_status}"

    def get_detail_url(self, obj):
        model = get_model_by_lodgement_number(obj["lodgement_number"])
        # If we need this for external details pages, we can add a check for the request here
        # change interal to external and make sure the external details page in the url conf takes pk as a kwarg rather
        # than <model_name>_pk
        return reverse(
            f"internal-{model._meta.model.__name__.lower()}-detail",
            kwargs={"pk": obj["id"]},
        )
