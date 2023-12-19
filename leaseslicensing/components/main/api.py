import logging

from django.apps import apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import F
from django.forms import ValidationError
from django.http import FileResponse, Http404
from rest_framework import status, views, viewsets
from rest_framework.decorators import action
from rest_framework.decorators import action as detail_route
from rest_framework.decorators import renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from reversion.errors import RevertError
from reversion.models import Version

from leaseslicensing import helpers
from leaseslicensing.components.main.decorators import basic_exception_handler
from leaseslicensing.components.main.models import (
    ApplicationType,
    Question,
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
    QuestionSerializer,
    SecureDocumentSerializer,
    TemporaryDocumentCollectionSerializer,
)
from leaseslicensing.permissions import IsInternalOrHasObjectPermission

logger = logging.getLogger(__name__)


class QuestionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


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
                secure_url=d.secure_url,
            )
            for d in instance.documents.all()
            if d._file
        ]
        return Response({"filedata": returned_file_data})


class KeyValueListMixin:
    @action(detail=False, methods=["get"], url_path="key-value-list")
    def key_value_list(self, request):
        if not hasattr(self, "key_value_display_field"):
            raise AttributeError("key_value_display_field is not defined on viewset")
        if not hasattr(self, "key_value_serializer_class"):
            raise AttributeError("key_value_serializer_class is not defined on viewset")

        queryset = self.get_queryset().only("id", self.key_value_display_field)
        search_term = request.GET.get("term", "")
        if search_term:
            queryset = queryset.filter(
                **{f"{self.key_value_display_field}__icontains": search_term}
            )[:30]
        serializer = self.key_value_serializer_class(queryset, many=True)
        return Response(serializer.data)


class Select2ListMixin:
    select2_search_case_sensitive = False
    """ For simplicity, uses the key_value_display_field to display the text in the select2
        Default behaviour is to be case insensitive.
        If you want to be case sensitive, set select2_search_case_sensitive to True in the
        viewset class
    """

    @action(detail=False, methods=["get"], url_path="select2-list")
    def select2_list(self, request):
        if not self.key_value_display_field:
            raise AttributeError("key_value_display_field is not defined on viewset")
        search_term = request.GET.get("term", "")
        queryset = (
            self.get_queryset()
            .annotate(text=F(self.key_value_display_field))
            .values("id", "text")
        )
        if self.select2_search_case_sensitive:
            results = queryset.filter(text__contains=search_term)[:10]
        else:
            results = queryset.filter(text__icontains=search_term)[:10]
        return Response({"results": results})


class NoPaginationListMixin:
    def get_paginated_response(self, data):
        if "no_pagination" == self.action:
            return data
        return super().get_paginated_response(data)

    @action(detail=False, methods=["get"], url_path="no-pagination")
    def no_pagination(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)


class LicensingViewset(viewsets.ModelViewSet):
    http_method_names = ["head", "get", "post", "put", "patch"]

    def destroy(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class ApplicationTypeViewSet(viewsets.ReadOnlyModelViewSet, KeyValueListMixin):
    queryset = ApplicationType.objects.all()
    serializer_class = ApplicationTypeSerializer
    key_value_display_field = "name"
    key_value_serializer_class = ApplicationTypeKeyValueSerializer


class UserActionLoggingViewset(LicensingViewset):
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
        response = super().create(request, *args, **kwargs)
        instance = response.data.serializer.instance
        instance.log_user_action(
            settings.ACTION_CREATE.format(
                instance._meta.verbose_name.title(),  # pylint: disable=protected-acces
                helpers.get_instance_identifier(instance),
            ),
            request,
        )
        return response

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


class SecureFileAPIView(views.APIView):
    """Allows permissioned and (optionally) versioned access to a file field on a model instance"""

    permission_classes = [IsInternalOrHasObjectPermission]

    def get(self, request, *args, **kwargs):
        model, instance_id, file_field_name, revision_id = (
            kwargs["model"],
            kwargs["instance_id"],
            kwargs["file_field_name"],
            kwargs.get("revision_id", None),
        )
        try:
            instance = apps.get_model(
                app_label="leaseslicensing", model_name=model
            ).objects.get(id=instance_id)
        except ObjectDoesNotExist:
            raise Http404
        else:
            if revision_id:
                versions = (
                    Version.objects.get_for_object(instance)
                    .filter(revision_id=revision_id)
                    .order_by("-revision__date_created")
                )

                first = versions.first()
                if not first:
                    return FileResponse({})
                try:
                    instance = first._object_version.object
                except RevertError:
                    logger.exception("Error reverting object version")
                    raise Http404

        self.check_object_permissions(request, instance)

        try:
            file = getattr(instance, file_field_name)
        except AttributeError:
            raise Http404

        if not file:
            raise Http404

        return FileResponse(file)


class SecureDocumentAPIView(views.APIView):
    """Allows permissioned access to a document that is attached to a model instance
    By default, this api view will look for the documents with a related name of 'documents'
    you can override this by passing a related_name in the url kwargs
    the file field on the document must be named '_file'
    """

    permission_classes = [IsInternalOrHasObjectPermission]

    def get(self, request, *args, **kwargs):
        logger.info("SecureDocumentAPIView")
        model, instance_id, document_id = (
            kwargs["model"],
            kwargs["instance_id"],
            kwargs["document_id"],
        )
        try:
            instance = apps.get_model(
                app_label="leaseslicensing", model_name=model
            ).objects.get(id=instance_id)
        except ObjectDoesNotExist:
            raise Http404

        self.check_object_permissions(request, instance)

        if kwargs["related_name"]:
            try:
                documents = getattr(instance, kwargs["related_name"])
            except AttributeError:
                raise ValidationError(
                    f"Related name {kwargs['related_name']} not found on {model}"
                )
        else:
            documents = instance.documents

        try:
            document = documents.get(id=document_id)
        except ObjectDoesNotExist:
            raise Http404

        try:
            file = getattr(document, "_file")
        except AttributeError:
            raise Http404

        if not file:
            raise Http404
        return FileResponse(file)


class SecureDocumentsAPIView(views.APIView):
    """Allows permissioned access to documents that are attached to a model instance
    By default, this api view will look for the documents with a related name of 'documents'
    you can override this by passing a related_name in the url kwargs (see: urls.py)
    the file field on the document must be named '_file' which is our standard
    """

    permission_classes = [IsInternalOrHasObjectPermission]
    serializer_class = SecureDocumentSerializer

    def get(self, request, *args, **kwargs):
        model, instance_id = (
            kwargs["model"],
            kwargs["instance_id"],
        )
        try:
            instance = apps.get_model(
                app_label="leaseslicensing", model_name=model
            ).objects.get(id=instance_id)
        except ObjectDoesNotExist:
            raise Http404

        self.check_object_permissions(request, instance)

        related_name = kwargs.get("related_name", None)
        if related_name:
            try:
                documents = getattr(instance, related_name)
            except AttributeError:
                raise ValidationError(
                    f"Related name {related_name} not found on {model}"
                )
        else:
            documents = instance.documents
            related_name = "documents"

        data = self.serializer_class(
            documents.all(),
            many=True,
            model=model,
            instance_id=instance_id,
            related_name=related_name,
        ).data

        return Response(data)
