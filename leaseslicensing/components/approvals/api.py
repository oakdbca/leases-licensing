import logging
import traceback
from datetime import datetime

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse
from rest_framework import filters, generics, serializers, views, viewsets
from rest_framework.decorators import action as detail_route
from rest_framework.decorators import action as list_route
from rest_framework.decorators import renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework_datatables.pagination import DatatablesPageNumberPagination
from rest_framework_datatables.renderers import DatatablesRenderer

from leaseslicensing.components.approvals.models import (
    Approval,
    ApprovalDocument,
    ApprovalType,
)
from leaseslicensing.components.approvals.serializers import (
    ApprovalCancellationSerializer,
    ApprovalDocumentHistorySerializer,
    ApprovalLogEntrySerializer,
    ApprovalPaymentSerializer,
    ApprovalSerializer,
    ApprovalSurrenderSerializer,
    ApprovalSuspensionSerializer,
    ApprovalUserActionSerializer,
)
from leaseslicensing.components.compliances.models import Compliance
from leaseslicensing.components.invoicing.serializers import InvoiceSerializer
from leaseslicensing.components.main.decorators import basic_exception_handler
from leaseslicensing.components.main.filters import LedgerDatatablesFilterBackend
from leaseslicensing.components.main.process_document import process_generic_document
from leaseslicensing.components.main.serializers import RelatedItemSerializer
from leaseslicensing.components.organisations.models import OrganisationContact
from leaseslicensing.components.proposals.api import ProposalRenderer
from leaseslicensing.components.proposals.models import ApplicationType, Proposal
from leaseslicensing.helpers import is_assessor, is_customer, is_internal

logger = logging.getLogger(__name__)


class GetApprovalTypesDict(views.APIView):
    renderer_classes = [
        JSONRenderer,
    ]

    def get(self, request, format=None):
        approval_types_dict = cache.get("approval_types_dict")
        if not approval_types_dict:
            approval_types_dict = [
                {
                    "id": t.id,
                    "name": t.name,
                    "details_placeholder": t.details_placeholder,
                    "approval_type_document_types": [
                        {
                            "id": doc_type_link.approval_type_document_type.id,
                            "name": doc_type_link.approval_type_document_type.name,
                            "mandatory": doc_type_link.mandatory,
                        }
                        # for doc_type in t.approvaltypedocumenttypes.all()
                        for doc_type_link in t.approvaltypedocumenttypeonapprovaltype_set.all()
                    ],
                }
                for t in ApprovalType.objects.all()
            ]
            cache.set(
                "approval_types_dict",
                approval_types_dict,
                settings.LOV_CACHE_TIMEOUT,
            )
        return Response(approval_types_dict)


class GetApprovalStatusesDict(views.APIView):
    renderer_classes = [
        JSONRenderer,
    ]

    def get(self, request, format=None):
        approval_statuses = cache.get(settings.CACHE_KEY_APPROVAL_STATUSES)
        if approval_statuses is None:
            approval_statuses = [
                {"code": i[0], "description": i[1]} for i in Approval.STATUS_CHOICES
            ]
            cache.set(
                settings.CACHE_KEY_APPROVAL_STATUSES,
                approval_statuses,
                settings.LOV_CACHE_TIMEOUT,
            )
        return Response(approval_statuses)


class ApprovalFilterBackend(LedgerDatatablesFilterBackend):
    """
    Custom filters
    """

    def filter_queryset(self, request, queryset, view):
        total_count = queryset.count()

        def get_choice(status, choices=Proposal.PROCESSING_STATUS_CHOICES):
            for i in choices:
                if i[1] == status:
                    return i[0]
            return None

        filter_approval_type = (
            request.GET.get("filter_approval_type")
            if request.GET.get("filter_approval_type") != "all"
            else ""
        )
        filter_approval_status = (
            request.GET.get("filter_approval_status")
            if request.GET.get("filter_approval_status") != "all"
            else ""
        )
        filter_approval_expiry_date_from = request.GET.get(
            "filter_approval_expiry_date_from"
        )
        filter_approval_expiry_date_to = request.GET.get(
            "filter_approval_expiry_date_to"
        )

        filter_approval_organisation = (
            request.GET.get("filter_approval_organisation")
            if request.GET.get("filter_approval_organisation") != "all"
            else ""
        )
        filter_approval_region = (
            request.GET.get("filter_approval_region")
            if request.GET.get("filter_approval_region") != "all"
            else ""
        )
        filter_approval_district = (
            request.GET.get("filter_approval_district")
            if request.GET.get("filter_approval_district") != "all"
            else ""
        )
        filter_approval_group = (
            request.GET.get("filter_approval_group")
            if request.GET.get("filter_approval_group") != "all"
            else ""
        )

        if filter_approval_type:
            filter_approval_type = int(filter_approval_type)
            logger.debug(f"filter_approval_type: {filter_approval_type}")
            queryset = queryset.filter(
                current_proposal__application_type=filter_approval_type
            )
        if filter_approval_status:
            queryset = queryset.filter(status=filter_approval_status)
        if filter_approval_expiry_date_from:
            filter_approval_expiry_date_from = datetime.strptime(
                filter_approval_expiry_date_from, "%Y-%m-%d"
            )
            queryset = queryset.filter(
                expiry_date__gte=filter_approval_expiry_date_from
            )
        if filter_approval_expiry_date_to:
            filter_approval_expiry_date_to = datetime.strptime(
                filter_approval_expiry_date_to, "%Y-%m-%d"
            )
            queryset = queryset.filter(expiry_date__lte=filter_approval_expiry_date_to)

        if filter_approval_organisation:
            filter_approval_organisation = int(filter_approval_organisation)
            logger.debug(
                f"filter_approval_organisation: {filter_approval_organisation}"
            )
            queryset = queryset.filter(org_applicant_id=filter_approval_organisation)
        if filter_approval_region:
            filter_approval_region = int(filter_approval_region)
            logger.debug(f"filter_approval_region: {filter_approval_region}")
            queryset = queryset.filter(
                current_proposal__localities__district__region_id=filter_approval_region
            )
        if filter_approval_district:
            filter_approval_district = int(filter_approval_district)
            logger.debug(f"filter_approval_district: {filter_approval_district}")
            queryset = queryset.filter(
                current_proposal__localities__district_id=filter_approval_district
            )
        if filter_approval_group:
            filter_approval_group = int(filter_approval_group)
            logger.debug(f"filter_approval_group: {filter_approval_group}")
            proposal_ids = (
                Proposal.objects.filter(groups__id__contains=filter_approval_group)
                .distinct()
                .values_list("id", flat=True)
            )
            queryset = queryset.filter(current_proposal__in=proposal_ids)

        # getter = request.query_params.get
        # fields = self.get_fields(getter)
        # ordering = self.get_ordering(getter, fields)
        queryset = self.apply_request(
            request, queryset, view, ledger_lookup_fields=["ind_applicant"]
        )
        setattr(view, "_datatables_total_count", total_count)
        return queryset


class ApprovalPaginatedViewSet(viewsets.ModelViewSet):
    # filter_backends = (ProposalFilterBackend,)
    filter_backends = (ApprovalFilterBackend,)
    pagination_class = DatatablesPageNumberPagination
    renderer_classes = (ProposalRenderer,)
    page_size = 10
    queryset = Approval.objects.none()
    serializer_class = ApprovalSerializer

    def get_queryset(self):
        if not is_internal(self.request) and not is_customer(self.request):
            return super().get_queryset()

        if is_internal(self.request):
            qs = Approval.objects.all()
        elif is_customer(self.request):
            # TODO: fix EmailUserRO issue here
            # user_orgs = [org.id for org in self.request.user.leaseslicensing_organisations.all()]
            # queryset =  Approval.objects.filter(Q(org_applicant_id__in = user_orgs)
            # | Q(submitter = self.request.user))
            qs = Approval.objects.filter(Q(submitter=self.request.user.id))

        target_email_user_id = self.request.query_params.get(
            "target_email_user_id", None
        )
        if (
            target_email_user_id
            and target_email_user_id.isnumeric()
            and int(target_email_user_id) > 0
        ):
            logger.debug(f"target_email_user_id: {target_email_user_id}")
            target_email_user_id = int(target_email_user_id)
            # TODO: Do we need to exclude org applications here? Would lead to no results
            # when the query is parametrized for user id and org id
            # qs = qs.exclude(org_applicant__isnull=False)
            qs = qs.filter(
                submitter=target_email_user_id
            )

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
            qs = qs.exclude(org_applicant__isnull=True).filter(
                org_applicant__id=target_organisation_id
            )

        target_compliance_id = self.request.query_params.get(
            "target_compliance_id", None
        )
        if (
            target_compliance_id
            and target_compliance_id.isnumeric()
            and int(target_compliance_id) > 0
        ):
            compliance = Compliance.objects.get(id=target_compliance_id)

            qs = qs.filter(id=compliance.approval_id)

        return qs

    #    def list(self, request, *args, **kwargs):
    #        response = super(ProposalPaginatedViewSet, self).list(request, args, kwargs)
    #
    #        # Add extra data to response.data
    #        #response.data['regions'] = self.get_queryset().filter
    # (region__isnull=False).values_list('region__name', flat=True).distinct()
    #        return response

    @list_route(
        methods=[
            "GET",
        ],
        detail=False,
    )
    def approvals_external(self, request, *args, **kwargs):
        """
        Paginated serializer for datatables - used by the internal and external dashboard
        (filtered by the get_queryset method)

        To test:
            http://localhost:8000/api/approval_paginated/approvals_external/?format=datatables&draw=1&length=2
        """

        # qs = self.queryset().order_by('lodgement_number', '-issue_date').distinct('lodgement_number')
        # qs = ProposalFilterBackend().filter_queryset(self.request, qs, self)

        ids = (
            self.get_queryset()
            .order_by("lodgement_number", "-issue_date")
            .distinct("lodgement_number")
            .values_list("id", flat=True)
        )
        qs = Approval.objects.filter(id__in=ids)
        qs = self.filter_queryset(qs)

        # on the internal organisations dashboard, filter the Proposal/Approval/Compliance datatables
        # by applicant/organisation
        applicant_id = request.GET.get("org_id")
        if applicant_id:
            qs = qs.filter(org_applicant_id=applicant_id)
        submitter_id = request.GET.get("submitter_id", None)
        if submitter_id:
            qs = qs.filter(submitter_id=submitter_id)

        self.paginator.page_size = qs.count()
        result_page = self.paginator.paginate_queryset(qs, request)
        serializer = ApprovalSerializer(
            result_page, context={"request": request}, many=True
        )
        return self.paginator.get_paginated_response(serializer.data)


class ApprovalPaymentFilterViewSet(generics.ListAPIView):
    """https://cop-internal.dbca.wa.gov.au/api/filtered_organisations?search=Org1"""

    queryset = Approval.objects.none()
    serializer_class = ApprovalPaymentSerializer
    filter_backends = (filters.SearchFilter,)
    # search_fields = ('applicant', 'applicant_id',)
    search_fields = ("id",)

    def get_queryset(self):
        """
        Return All approvals associated with user (proxy_applicant and org_applicant)
        """
        # return Approval.objects.filter(proxy_applicant=self.request.user)
        user = self.request.user

        # get all orgs associated with user
        user_org_ids = OrganisationContact.objects.filter(email=user.email).values_list(
            "organisation_id", flat=True
        )

        now = datetime.now().date()
        approval_qs = Approval.objects.filter(
            Q(proxy_applicant=user)
            | Q(org_applicant_id__in=user_org_ids)
            | Q(submitter_id=user)
        )
        approval_qs = approval_qs.exclude(expiry_date__lt=now)
        approval_qs = approval_qs.exclude(
            replaced_by__isnull=False
        )  # get lastest licence, ignore the amended
        return approval_qs

    @list_route(
        methods=[
            "GET",
        ],
        detail=False,
    )
    def _list(self, request, *args, **kwargs):
        data = []
        for approval in self.get_queryset():
            data.append(
                dict(
                    lodgement_number=approval.lodgement_number,
                    current_proposal=approval.current_proposal_id,
                )
            )
        return Response(data)
        # return Response(self.get_queryset().values_list('lodgement_number','current_proposal_id'))


class ApprovalViewSet(viewsets.ModelViewSet):
    # queryset = Approval.objects.all()
    queryset = Approval.objects.none()
    serializer_class = ApprovalSerializer
    pagination_class = DatatablesPageNumberPagination

    def get_queryset(self):
        if is_internal(self.request):
            return Approval.objects.all()
        elif is_customer(self.request):
            user_orgs = (
                [
                    org.id
                    for org in self.request.user.leaseslicensing_organisations.all()
                ]
                if hasattr(self.request.user, "leaseslicensing_organisations")
                else []
            )
            queryset = Approval.objects.filter(
                Q(org_applicant_id__in=user_orgs) | Q(submitter=self.request.user.id)
            )
            return queryset
        return Approval.objects.none()

    def list(self, request, *args, **kwargs):
        # queryset = self.get_queryset()
        queryset = (
            self.get_queryset()
            .order_by("lodgement_number", "-issue_date")
            .distinct("lodgement_number")
        )
        # Filter by org
        org_id = request.GET.get("org_id", None)
        if org_id:
            queryset = queryset.filter(org_applicant_id=org_id)
        submitter_id = request.GET.get("submitter_id", None)
        if submitter_id:
            queryset = queryset.filter(submitter_id=submitter_id)
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
        # region_qs =  self.get_queryset().filter(current_proposal__region__isnull=False)
        # .values_list('current_proposal__region__name', flat=True).distinct()
        # activity_qs =  self.get_queryset().filter(current_proposal__activity__isnull=False)
        # .values_list('current_proposal__activity', flat=True).distinct()
        application_types = ApplicationType.objects.all().values_list("name", flat=True)
        data = dict(
            approval_status_choices=[i[1] for i in Approval.STATUS_CHOICES],
            application_types=application_types,
        )
        return Response(data)

    @detail_route(methods=["POST"], detail=True)
    @renderer_classes((JSONRenderer,))
    @basic_exception_handler
    def process_approval_cancellation_document(self, request, *args, **kwargs):
        instance = self.get_object()
        returned_data = process_generic_document(
            request, instance, document_type="approval_cancellation_document"
        )
        if returned_data:
            return Response(returned_data)
        else:
            return Response()

    @detail_route(methods=["POST"], detail=True)
    @renderer_classes((JSONRenderer,))
    @basic_exception_handler
    def process_approval_surrender_document(self, request, *args, **kwargs):
        instance = self.get_object()
        returned_data = process_generic_document(
            request, instance, document_type="approval_surrender_document"
        )
        if returned_data:
            return Response(returned_data)
        else:
            return Response()

    @detail_route(methods=["POST"], detail=True)
    @renderer_classes((JSONRenderer,))
    @basic_exception_handler
    def process_approval_suspension_document(self, request, *args, **kwargs):
        instance = self.get_object()
        returned_data = process_generic_document(
            request, instance, document_type="approval_suspension_document"
        )
        if returned_data:
            return Response(returned_data)
        else:
            return Response()

    @detail_route(
        methods=[
            "POST",
        ],
        detail=True,
    )
    @basic_exception_handler
    def approval_cancellation(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ApprovalCancellationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance.approval_cancellation(request, serializer.validated_data)
        serializer = ApprovalSerializer(instance, context={"request": request})
        return Response(serializer.data)

    @detail_route(
        methods=[
            "POST",
        ],
        detail=True,
    )
    @basic_exception_handler
    def approval_suspension(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ApprovalSuspensionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance.approval_suspension(request, serializer.validated_data)
        serializer = ApprovalSerializer(instance, context={"request": request})
        return Response(serializer.data)

    @detail_route(
        methods=[
            "POST",
        ],
        detail=True,
    )
    @basic_exception_handler
    def approval_reinstate(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.reinstate_approval(request)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @detail_route(
        methods=[
            "POST",
        ],
        detail=True,
    )
    @basic_exception_handler
    def approval_surrender(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ApprovalSurrenderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance.approval_surrender(request, serializer.validated_data)
        serializer = ApprovalSerializer(instance, context={"request": request})
        return Response(serializer.data)

    @detail_route(
        methods=[
            "POST",
        ],
        detail=True,
    )
    @basic_exception_handler
    def review_renewal(self, request, *args, **kwargs):
        if not is_assessor(request):
            raise serializers.ValidationError(
                "You do not have permission to perform this action."
            )

        instance = self.get_object()

        can_be_renewed = request.data.get("can_be_renewed", None)
        if can_be_renewed is None:
            raise serializers.ValidationError(
                "Expecting a boolean value can_be_renewed in POST"
            )

        instance.review_renewal(can_be_renewed)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @detail_route(
        methods=[
            "PATCH",
        ],
        detail=True,
    )
    @basic_exception_handler
    def review_invoice_details(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.status = Approval.APPROVAL_STATUS_CURRENT_EDITING_INVOICING
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @detail_route(
        methods=[
            "PATCH",
        ],
        detail=True,
    )
    @basic_exception_handler
    def cancel_editing_invoicing(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.status = Approval.APPROVAL_STATUS_CURRENT
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @detail_route(
        methods=[
            "GET",
        ],
        detail=True,
    )
    @basic_exception_handler
    def approval_history(self, request, *args, **kwargs):
        instance = self.get_object()
        approval_documents = ApprovalDocument.objects.filter(
            approval__lodgement_number=instance.lodgement_number,
            name__icontains="approval",
        ).order_by("-uploaded_date")
        serializer = ApprovalDocumentHistorySerializer(approval_documents, many=True)
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
        serializer = ApprovalUserActionSerializer(qs, many=True)
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
        serializer = ApprovalLogEntrySerializer(qs, many=True)
        return Response(serializer.data)

    @detail_route(
        methods=[
            "POST",
        ],
        detail=True,
    )
    @renderer_classes((JSONRenderer,))
    def add_comms_log(self, request, *args, **kwargs):
        with transaction.atomic():
            instance = self.get_object()
            mutable = request.data._mutable
            request.data._mutable = True
            request.data["approval"] = f"{instance.id}"
            request.data["staff"] = f"{request.user.id}"
            request.data._mutable = mutable
            serializer = ApprovalLogEntrySerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            comms = serializer.save()

            # Save the files
            for f in request.FILES.getlist("files"):
                document = comms.documents.create()
                document.name = str(f)
                document._file = f
                document.save()

            return Response(serializer.data)

    @detail_route(
        methods=[
            "GET",
        ],
        detail=True,
    )
    def invoices(self, request, *args, **kwargs):
        instance = self.get_object()
        qs = instance.invoices.all()
        serializer = InvoiceSerializer(qs, many=True, context={"request": request})
        return Response(serializer.data)

    @detail_route(
        methods=["GET"],
        detail=True,
        renderer_classes=[DatatablesRenderer],
        pagination_class=DatatablesPageNumberPagination,
    )
    def related_items(self, request, *args, **kwargs):
        """Uses union to combine a queryset of multiple different model types
        and uses a generic related item serializer to return the data
        Todo: Pagination is not working."""
        instance = self.get_object()
        proposals_queryset = Proposal.objects.filter(
            approval__lodgement_number=instance.lodgement_number
        ).values("id", "lodgement_number", "processing_status")
        compliances_queryset = instance.compliances.values(
            "id", "lodgement_number", "processing_status"
        )
        queryset = proposals_queryset.union(compliances_queryset).order_by(
            "lodgement_number"
        )

        # page = self.paginate_queryset(queryset)
        # if page is not None:
        #     logger.debug(f"page = {page}")
        #     serializer = RelatedItemSerializer(page, many=True)
        #     return self.get_paginated_response(serializer.data)

        logger.debug(f"paginated_queryset query: {queryset}")
        serializer = RelatedItemSerializer(queryset, many=True)
        data = {}
        # Add the fields that the datatables renderer expects
        data["data"] = serializer.data
        data["recordsFiltered"] = queryset.count()
        data["recordsTotal"] = queryset.count()
        return Response(data=data)
