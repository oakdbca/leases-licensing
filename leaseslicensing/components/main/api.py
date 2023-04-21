import logging

from django.conf import settings
from django.db import transaction
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.decorators import action as detail_route
from rest_framework.decorators import renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from leaseslicensing import helpers
from leaseslicensing.components.main.decorators import basic_exception_handler
from leaseslicensing.components.main.models import (
    ApplicationType,
    GlobalSettings,
    MapLayer,
    Question,
    RequiredDocument,
    TemporaryDocumentCollection,
)
from leaseslicensing.components.main.process_document import (
    cancel_document,
    delete_document,
    save_document,
)
from leaseslicensing.components.main.serializers import (
    ApplicationTypeKeyValueSerializer,
    ApplicationTypeSerializer,
    GlobalSettingsSerializer,
    MapLayerSerializer,
    QuestionSerializer,
    RequiredDocumentSerializer,
    TemporaryDocumentCollectionSerializer,
)
from leaseslicensing.helpers import is_customer, is_internal

logger = logging.getLogger(__name__)


class GlobalSettingsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = GlobalSettings.objects.all().order_by("id")
    serializer_class = GlobalSettingsSerializer


class RequiredDocumentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RequiredDocument.objects.all()
    serializer_class = RequiredDocumentSerializer


class QuestionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class MapLayerViewSet(viewsets.ModelViewSet):
    queryset = MapLayer.objects.none()
    serializer_class = MapLayerSerializer

    def get_queryset(self):
        if is_internal(self.request):
            return MapLayer.objects.filter(option_for_internal=True)
        elif is_customer(self.request):
            return MapLayer.objects.filter(option_for_external=True)
        return MapLayer.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class TemporaryDocumentCollectionViewSet(viewsets.ModelViewSet):
    queryset = TemporaryDocumentCollection.objects.all()
    serializer_class = TemporaryDocumentCollectionSerializer

    @basic_exception_handler
    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            serializer = TemporaryDocumentCollectionSerializer(
                data=request.data,
            )
            serializer.is_valid(raise_exception=True)
            if serializer.is_valid():
                instance = serializer.save()
                save_document(
                    request, instance, comms_instance=None, document_type=None
                )

                return Response(serializer.data)

    @detail_route(methods=["POST"], detail=True)
    @renderer_classes((JSONRenderer,))
    @basic_exception_handler
    def process_temp_document(self, request, *args, **kwargs):
        instance = self.get_object()
        action = request.data.get("action")

        if action == "list":
            pass

        elif action == "delete":
            delete_document(
                request, instance, comms_instance=None, document_type="temp_document"
            )

        elif action == "cancel":
            cancel_document(
                request, instance, comms_instance=None, document_type="temp_document"
            )

        elif action == "save":
            save_document(
                request, instance, comms_instance=None, document_type="temp_document"
            )

        returned_file_data = [
            dict(
                file=d._file.url,
                id=d.id,
                name=d.name,
            )
            for d in instance.documents.all()
            if d._file
        ]
        return Response({"filedata": returned_file_data})


class KeyValueListMixin:
    @action(detail=False, methods=["get"], url_path="key-value-list")
    def key_value_list(self, request):
        if not self.key_value_display_field:
            raise AttributeError("key_value_display_field is not defined on viewset")
        if not self.key_value_serializer_class:
            raise AttributeError("key_value_serializer_class is not defined on viewset")

        serializer = self.key_value_serializer_class(
            self.get_queryset().only("id", self.key_value_display_field), many=True
        )
        return Response(serializer.data)


class NoPaginationListMixin:
    def get_paginated_response(self, data):
        if "no_pagination" == self.action:
            return data
        return super().get_paginated_response(data)

    @action(detail=False, methods=["get"], url_path="no-pagination")
    def no_pagination(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)


class ApplicationTypeViewSet(viewsets.ReadOnlyModelViewSet, KeyValueListMixin):
    queryset = ApplicationType.objects.all()
    serializer_class = ApplicationTypeSerializer
    key_value_display_field = "name"
    key_value_serializer_class = ApplicationTypeKeyValueSerializer


class UserActionLoggingViewset(viewsets.ModelViewSet):
    """Class that extends the ModelViewSet to log the common user actions

    will scan the instance provided for the fields listed in settings
    use the first one it finds. If it doesn't find one it will raise an AttributeError.
    """

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.log_user_action(
            settings.ACTION_VIEW.format(
                instance._meta.verbose_name.title(),  # pylint: disable=protected-access
                helpers.get_instance_identifier(instance),
            ),
            request,
        )
        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.log_user_action(
            settings.ACTION_CREATE.format(
                instance._meta.verbose_name.title(),  # pylint: disable=protected-acces
                helpers.get_instance_identifier(instance),
            ),
            request,
        )
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.log_user_action(
            settings.ACTION_UPDATE.format(
                instance._meta.verbose_name.title(),  # pylint: disable=protected-access
                helpers.get_instance_identifier(instance),
            ),
            request,
        )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.log_user_action(
            settings.ACTION_DESTROY.format(
                instance._meta.verbose_name.title(),  # pylint: disable=protected-access
                helpers.get_instance_identifier(instance),
            ),
            request,
        )
        return super().destroy(request, *args, **kwargs)
