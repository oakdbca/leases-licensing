from datetime import datetime
from django.db import transaction
from rest_framework import viewsets
from rest_framework import viewsets, views
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework_datatables.filters import DatatablesFilterBackend

from leaseslicensing.components.competitive_processes.models import CompetitiveProcess
from leaseslicensing.components.competitive_processes.serializers import CompetitiveProcessLogEntrySerializer, \
    CompetitiveProcessUserActionSerializer, ListCompetitiveProcessSerializer, \
    CompetitiveProcessSerializer
from leaseslicensing.components.main.filters import LedgerDatatablesFilterBackend
from leaseslicensing.components.main.process_document import process_generic_document
from leaseslicensing.components.main.related_item import RelatedItemsSerializer
from leaseslicensing.components.competitive_processes.utils import save_geometry
from leaseslicensing.helpers import is_internal
from rest_framework.decorators import (
    action as detail_route,
    renderer_classes,
    parser_classes,
)
from leaseslicensing.components.main.decorators import basic_exception_handler


class CompetitiveProcessFilterBackend(LedgerDatatablesFilterBackend):

    def filter_queryset(self, request, queryset, view):
        filter_status = request.GET.get("filter_status") if request.GET.get("filter_status") != "all" else ""
        filter_competitive_process_created_from = request.GET.get("filter_competitive_process_created_from")
        filter_competitive_process_created_to = request.GET.get("filter_competitive_process_created_to")

        if filter_status:
            queryset = queryset.filter(status=filter_status)
        if filter_competitive_process_created_from:
            filter_competitive_process_created_from = datetime.strptime(filter_competitive_process_created_from, "%Y-%m-%d")
            queryset = queryset.filter(created_at__gte=filter_competitive_process_created_from)
        if filter_competitive_process_created_to:
            filter_competitive_process_created_to = datetime.strptime(filter_competitive_process_created_to, "%Y-%m-%d")
            queryset = queryset.filter(created_at__lte=filter_competitive_process_created_to)

        queryset = self.apply_request(request, queryset, view,
                                            model=CompetitiveProcess,)

        # setattr(view, "_datatables_total_count", total_count)
        return queryset


class CompetitiveProcessViewSet(viewsets.ModelViewSet):
    queryset = CompetitiveProcess.objects.none()
    filter_backends = (CompetitiveProcessFilterBackend,)

    def get_serializer_class(self):
        """ Configure serializers to use """
        if self.action == 'list':
            return ListCompetitiveProcessSerializer
        return CompetitiveProcessSerializer

    @basic_exception_handler
    def get_queryset(self):
        if is_internal(self.request):
            return CompetitiveProcess.objects.all()
        else:
            return CompetitiveProcess.objects.none()

    @detail_route(methods=["POST",], detail=True,)
    @renderer_classes((JSONRenderer,))
    @basic_exception_handler
    def complete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_update(instance, request)
        # serializer = self.get_serializer(instance, data=request.data['competitive_process'])
        # serializer.is_valid(raise_exception=True)
        # instance = serializer.save()

        instance.complete(request)
        return Response({})

    @detail_route(methods=["POST",], detail=True,)
    @renderer_classes((JSONRenderer,))
    @basic_exception_handler
    def discard(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_update(instance, request)
        # serializer = self.get_serializer(instance, data=request.data['competitive_process'])
        # serializer.is_valid(raise_exception=True)
        # instance = serializer.save()

        instance.discard(request)
        return Response({})

    @detail_route(methods=["POST"], detail=True)
    @renderer_classes((JSONRenderer,))
    @basic_exception_handler
    def process_shapefile_document(self, request, *args, **kwargs):

        # TODO: implement

        return Response({})

    @basic_exception_handler
    def list(self, request, *args, **kwargs):
        # TODO Can this be done shorter and in one line
        qs = self.get_queryset()
        qs = self.filter_queryset(qs)

        qs = qs.distinct()
        self.paginator.page_size = qs.count()
        result_page = self.paginator.paginate_queryset(qs, request)
        serializer = self.get_serializer(result_page, context={"request": request}, many=True)
        return self.paginator.get_paginated_response(serializer.data)

    @basic_exception_handler
    def retrieve(self, request, *args, **kwargs):
        competitive_process = self.get_object()
        serializer = self.get_serializer(competitive_process, context={'request': request})
        return Response(serializer.data)

    @basic_exception_handler
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_update(instance, request)

        return Response({})

    def perform_update(self, instance, request):
        competitive_process_data = request.data.get('competitive_process', None)
        # Pop "geometry" data to handle it independently of the "competitive process"
        competitive_process_geometry_data = competitive_process_data.pop('competitive_process_geometries', None)
        # Handle "competitive process"
        serializer = self.get_serializer(instance, data=competitive_process_data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        # Handle "geometry" data
        if competitive_process_geometry_data:
            save_geometry(instance, competitive_process_geometry_data, self.action)

    @detail_route(methods=["GET",], detail=True,)
    @basic_exception_handler
    def action_log(self, request, *args, **kwargs):
        instance = self.get_object()
        qs = instance.action_logs.all()
        serializer = CompetitiveProcessUserActionSerializer(qs, many=True)
        return Response(serializer.data)

    @detail_route(methods=["GET",], detail=True,)
    @basic_exception_handler
    def comms_log(self, request, *args, **kwargs):
        instance = self.get_object()
        qs = instance.comms_logs.all()
        serializer = CompetitiveProcessLogEntrySerializer(qs, many=True)
        return Response(serializer.data)

    @detail_route(methods=["POST",], detail=True,)
    @renderer_classes((JSONRenderer,))
    @basic_exception_handler
    def add_comms_log(self, request, *args, **kwargs):
        with transaction.atomic():
            instance = self.get_object()
            mutable = request.data._mutable
            request.data._mutable = True
            request.data["proposal"] = "{}".format(instance.id)
            request.data["staff"] = "{}".format(request.user.id)
            request.data._mutable = mutable
            serializer = CompetitiveProcessLogEntrySerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            comms = serializer.save()
            # Save the files
            for f in request.FILES:
                document = comms.documents.create()
                document.name = str(request.FILES[f])
                document._file = request.FILES[f]
                document.save()
            # End Save Documents

            return Response(serializer.data)

    @detail_route(methods=["POST"], detail=True)
    @renderer_classes((JSONRenderer,))
    @basic_exception_handler
    def process_competitive_process_document(self, request, *args, **kwargs):
        instance = self.get_object()
        returned_data = process_generic_document(
            request, instance, document_type="competitive_process_document"
        )
        if returned_data:
            return Response(returned_data)
        else:
            return Response()

    @detail_route(methods=["get"], detail=True)
    @basic_exception_handler
    def get_related_items(self, request, *args, **kwargs):
        instance = self.get_object()
        related_items = instance.get_related_items()
        serializer = RelatedItemsSerializer(related_items, many=True)
        return Response(serializer.data)


class GetCompetitiveProcessStatusesDict(views.APIView):
    renderer_classes = [
        JSONRenderer,
    ]

    def get(self, request, format=None):
        data = [{"id": i[0], "text": i[1]} for i in CompetitiveProcess.STATUS_CHOICES]
        return Response(data)
