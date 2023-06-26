import logging
import traceback
from copy import deepcopy
from datetime import datetime

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import transaction
from django.db.models import Q
from rest_framework import serializers, views, viewsets
from rest_framework.decorators import action as detail_route
from rest_framework.decorators import action as list_route
from rest_framework.decorators import renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework_datatables.pagination import DatatablesPageNumberPagination

from leaseslicensing.components.compliances.models import (
    Compliance,
    ComplianceAmendmentReason,
    ComplianceAmendmentRequest,
)
from leaseslicensing.components.compliances.serializers import (
    CompAmendmentRequestDisplaySerializer,
    ComplianceActionSerializer,
    ComplianceAmendmentRequestSerializer,
    ComplianceCommsSerializer,
    ComplianceSerializer,
    InternalComplianceSerializer,
    SaveComplianceSerializer,
)
from leaseslicensing.components.main.decorators import basic_exception_handler
from leaseslicensing.components.main.filters import LedgerDatatablesFilterBackend
from leaseslicensing.components.main.models import ApplicationType
from leaseslicensing.components.proposals.api import ProposalRenderer
from leaseslicensing.helpers import is_customer, is_internal

logger = logging.getLogger(__name__)


class GetComplianceStatusesDict(views.APIView):
    renderer_classes = [
        JSONRenderer,
    ]

    def get(self, request, format=None):
        data = [
            {"code": i[0], "description": i[1]}
            for i in Compliance.PROCESSING_STATUS_CHOICES
        ]
        return Response(data)


class GetComplianceCustomerStatusesDict(views.APIView):
    renderer_classes = [
        JSONRenderer,
    ]

    def get(self, request, format=None):
        data = [
            {"code": i[0], "description": i[1]}
            for i in Compliance.CUSTOMER_STATUS_CHOICES
        ]
        return Response(data)


class ComplianceFilterBackend(LedgerDatatablesFilterBackend):
    """
    Custom filters
    """

    def filter_queryset(self, request, queryset, view):
        total_count = queryset.count()

        filter_due_date_from = request.GET.get("filter_due_date_from")
        filter_due_date_to = request.GET.get("filter_due_date_to")
        filter_compliance_status = (
            request.GET.get("filter_compliance_status")
            if request.GET.get("filter_compliance_status") != "all"
            else ""
        )
        filter_application_type = (
            request.GET.get("filter_application_type")
            if request.GET.get("filter_application_type") != "all"
            else ""
        )

        if filter_due_date_from:
            filter_due_date_from = datetime.strptime(filter_due_date_from, "%Y-%m-%d")
            queryset = queryset.filter(due_date__gte=filter_due_date_from)
        if filter_due_date_to:
            filter_due_date_to = datetime.strptime(filter_due_date_to, "%Y-%m-%d")
            queryset = queryset.filter(due_date__lte=filter_due_date_to)
        if filter_compliance_status:
            queryset = queryset.filter(processing_status=filter_compliance_status)
        if filter_application_type:
            filter_application_type = int(filter_application_type)
            queryset = queryset.filter(
                proposal__application_type=filter_application_type
            )

        queryset = self.apply_request(
            request, queryset, view, ledger_lookup_fields=["ind_applicant"]
        )

        setattr(view, "_datatables_total_count", total_count)
        return queryset


class CompliancePaginatedViewSet(viewsets.ModelViewSet):
    filter_backends = (ComplianceFilterBackend,)
    pagination_class = DatatablesPageNumberPagination
    renderer_classes = (ProposalRenderer,)
    page_size = 10
    queryset = Compliance.objects.none()
    serializer_class = ComplianceSerializer

    def get_queryset(self):
        if not is_internal(self.request) and not is_customer(self.request):
            return Compliance.objects.none()

        if is_internal(self.request):
            qs = Compliance.objects.all().exclude(processing_status="discarded")

        elif is_customer(self.request):
            # TODO: fix EmailUserRO issue here
            # user_orgs = [org.id for org in self.request.user.leaseslicensing_organisations.all()]
            # queryset =  Compliance.objects.filter( Q(proposal__org_applicant_id__in = user_orgs) |
            # Q(proposal__submitter = self.request.user) ).exclude(processing_status='discarded')
            qs = Compliance.objects.filter(
                Q(proposal__submitter=self.request.user.id)
            ).exclude(processing_status="discarded")

        target_organisation_id = self.request.query_params.get(
            "target_organisation_id", None
        )
        if (
            target_organisation_id
            and target_organisation_id.isnumeric()
            and int(target_organisation_id) > 0
        ):
            logger.debug(f"target_organisation_id: {target_organisation_id}")
            target_organisation_id = int(target_organisation_id)
            qs = qs.exclude(approval__org_applicant__isnull=True).filter(
                approval__org_applicant__id=target_organisation_id
            )

        compliances_referred_to_me = self.request.query_params.get(
            "compliances_referred_to_me", False
        )
        if compliances_referred_to_me:
            # Todo: Once compliance referrals are completed use this to filter
            # compliances that are referred to the request user
            pass

        return qs

    @list_route(
        methods=[
            "GET",
        ],
        detail=False,
    )
    def list_external(self, request, *args, **kwargs):
        """
        User is accessing /external/ page
        """
        qs = self.get_queryset()
        qs = self.filter_queryset(qs)

        self.paginator.page_size = qs.count()
        result_page = self.paginator.paginate_queryset(qs, request)
        serializer = ComplianceSerializer(
            result_page, context={"request": request}, many=True
        )
        result = self.paginator.get_paginated_response(serializer.data)
        return result

    @list_route(
        methods=[
            "GET",
        ],
        detail=False,
    )
    def compliances_external(self, request, *args, **kwargs):
        """
        Paginated serializer for datatables - used by the external dashboard

        To test:
            http://localhost:8000/api/compliance_paginated/compliances_external/?format=datatables&draw=1&length=2
        """

        qs = self.get_queryset().exclude(processing_status="future")
        # qs = ProposalFilterBackend().filter_queryset(self.request, qs, self)
        qs = self.filter_queryset(qs)
        # qs = qs.order_by('lodgement_number', '-issue_date').distinct('lodgement_number')

        # on the internal organisations dashboard, filter the Proposal/Approval/Compliance datatables
        # by applicant/organisation
        applicant_id = request.GET.get("org_id")
        if applicant_id:
            qs = qs.filter(proposal__org_applicant_id=applicant_id)
        submitter_id = request.GET.get("submitter_id", None)
        if submitter_id:
            qs = qs.filter(proposal__submitter_id=submitter_id)
        self.paginator.page_size = qs.count()
        result_page = self.paginator.paginate_queryset(qs, request)
        serializer = ComplianceSerializer(
            result_page, context={"request": request}, many=True
        )
        return self.paginator.get_paginated_response(serializer.data)


class ComplianceViewSet(viewsets.ModelViewSet):
    serializer_class = ComplianceSerializer
    # queryset = Compliance.objects.all()
    queryset = Compliance.objects.none()

    def get_queryset(self):
        if is_internal(self.request):
            return Compliance.objects.all().exclude(processing_status="discarded")
        elif is_customer(self.request):
            # TODO: fix EmailUserRO issue here
            # user_orgs = [org.id for org in self.request.user.leaseslicensing_organisations.all()]
            # queryset =  Compliance.objects.filter( Q(proposal__org_applicant_id__in = user_orgs) |
            # Q(proposal__submitter = self.request.user) ).exclude(processing_status='discarded')
            queryset = Compliance.objects.filter(
                Q(proposal__submitter=self.request.user.id)
            ).exclude(processing_status="discarded")
            return queryset
        return Compliance.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        # Filter by org
        org_id = request.GET.get("org_id", None)
        if org_id:
            queryset = queryset.filter(proposal__org_applicant_id=org_id)
        submitter_id = request.GET.get("submitter_id", None)
        if submitter_id:
            queryset = queryset.filter(proposal__submitter_id=submitter_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @list_route(
        methods=[
            "GET",
        ],
        detail=False,
    )
    def filter_list(self, request, *args, **kwargs):
        """Used by the external dashboard filters"""
        region_qs = (
            self.get_queryset()
            .filter(proposal__region__isnull=False)
            .values_list("proposal__region__name", flat=True)
            .distinct()
        )
        activity_qs = (
            self.get_queryset()
            .filter(proposal__activity__isnull=False)
            .values_list("proposal__activity", flat=True)
            .distinct()
        )
        application_types = ApplicationType.objects.all().values_list("name", flat=True)
        data = dict(
            regions=region_qs,
            activities=activity_qs,
            application_types=application_types,
        )
        return Response(data)

    @detail_route(
        methods=[
            "GET",
        ],
        detail=True,
    )
    def internal_compliance(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = InternalComplianceSerializer(
            instance, context={"request": request}
        )
        return Response(serializer.data)

    @detail_route(
        methods=[
            "POST",
        ],
        detail=True,
    )
    @renderer_classes((JSONRenderer,))
    @basic_exception_handler
    def submit(self, request, *args, **kwargs):
        with transaction.atomic():
            instance = self.get_object()
            data = {
                "text": request.data.get("detail"),
            }

            serializer = SaveComplianceSerializer(instance, data=data)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            # FIXME Is the right place to submit the request. Invoking submit will also
            # send out email notifications,
            # so it would be plausible to do this last after everything else, but submitting
            # at the end of this function
            # will cause any document attached to this Compliance to be uploaded twice
            # and appear twice in the view.
            instance.submit(request)

            serializer = self.get_serializer(instance)

            logger.debug(f"num_files: {request.data.get('num_files')}")

            num_files = request.data.get("num_files")
            for i in range(int(num_files)):
                filename = request.data.get("name" + str(i))
                _file = request.data.get("file" + str(i))

                if not isinstance(_file, InMemoryUploadedFile):
                    raise serializers.ValidationError("No files attached")

                document = instance.documents.get_or_create(name=filename)[0]
                document.save()

            return Response(serializer.data)

    @detail_route(
        methods=[
            "GET",
        ],
        detail=True,
    )
    @basic_exception_handler
    def assign_request_user(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.assign_to(request.user.id, request)
        serializer = InternalComplianceSerializer(instance)
        return Response(serializer.data)

    @detail_route(
        methods=[
            "POST",
        ],
        detail=True,
    )
    @basic_exception_handler
    def delete_document(self, request, *args, **kwargs):
        instance = self.get_object()
        doc = request.data.get("document")
        instance.delete_document(request, doc)
        serializer = ComplianceSerializer(instance)
        return Response(serializer.data)

    @detail_route(
        methods=[
            "POST",
        ],
        detail=True,
    )
    @basic_exception_handler
    def assign_to(self, request, *args, **kwargs):
        instance = self.get_object()
        user_id = request.data.get("user_id", None)
        if not user_id:
            raise serializers.ValiationError("A user id is required")
        instance.assign_to(user_id, request)
        serializer = InternalComplianceSerializer(instance)
        return Response(serializer.data)

    @detail_route(
        methods=[
            "GET",
        ],
        detail=True,
    )
    @basic_exception_handler
    def unassign(self, request, *args, **kwargs):
        logger.debug("unassign")
        instance = self.get_object()
        instance.unassign(request)
        serializer = InternalComplianceSerializer(instance)
        return Response(serializer.data)

    @detail_route(
        methods=[
            "GET",
        ],
        detail=True,
    )
    @basic_exception_handler
    def accept(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.accept(request)
        serializer = InternalComplianceSerializer(instance)
        return Response(serializer.data)

    @detail_route(
        methods=[
            "GET",
        ],
        detail=True,
    )
    @basic_exception_handler
    def amendment_request(self, request, *args, **kwargs):
        instance = self.get_object()
        qs = instance.amendment_requests
        qs = qs.filter(status="requested")
        serializer = CompAmendmentRequestDisplaySerializer(qs, many=True)
        return Response(serializer.data)

    @detail_route(
        methods=[
            "GET",
        ],
        detail=True,
    )
    @basic_exception_handler
    def action_log(self, request, *args, **kwargs):
        instance = self.get_object()
        qs = instance.action_logs.all()
        serializer = ComplianceActionSerializer(qs, many=True)
        return Response(serializer.data)

    @detail_route(
        methods=[
            "GET",
        ],
        detail=True,
    )
    @basic_exception_handler
    def comms_log(self, request, *args, **kwargs):
        instance = self.get_object()
        qs = instance.comms_logs.all()
        serializer = ComplianceCommsSerializer(qs, many=True)
        return Response(serializer.data)

    @detail_route(
        methods=[
            "POST",
        ],
        detail=True,
    )
    @renderer_classes((JSONRenderer,))
    @basic_exception_handler
    def add_comms_log(self, request, *args, **kwargs):
        with transaction.atomic():
            instance = self.get_object()
            mutable = request.data._mutable
            request.data._mutable = True
            request.data["compliance"] = f"{instance.id}"
            request.data["staff"] = f"{request.user.id}"
            request.data._mutable = mutable
            serializer = ComplianceCommsSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            comms = serializer.save()

            # Save the files
            for f in request.FILES.getlist("files"):
                document = comms.documents.create()
                document.name = str(f)
                document._file = f
                document.save()

            return Response(serializer.data)


class ComplianceAmendmentRequestViewSet(viewsets.ModelViewSet):
    queryset = ComplianceAmendmentRequest.objects.all()
    serializer_class = ComplianceAmendmentRequestSerializer

    @basic_exception_handler
    def create(self, request, *args, **kwargs):
        request_data = deepcopy(request.data)
        request_data.update({"officer": request.user.id})
        serializer = self.get_serializer(data=request_data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        instance.generate_amendment(request)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class ComplianceAmendmentReasonChoicesView(views.APIView):
    renderer_classes = [
        JSONRenderer,
    ]

    def get(self, request, format=None):
        choices_list = []
        choices = ComplianceAmendmentReason.objects.all()
        if choices:
            for c in choices:
                choices_list.append({"key": c.id, "value": c.reason})
        return Response(choices_list)
