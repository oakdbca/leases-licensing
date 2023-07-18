import logging
from datetime import datetime
from decimal import Decimal

from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework_datatables.filters import DatatablesFilterBackend

from leaseslicensing.components.invoicing.models import (
    CPICalculationMethod,
    Invoice,
    InvoiceTransaction,
)
from leaseslicensing.components.invoicing.serializers import (
    CPICalculationMethodSerializer,
    InvoiceEditOracleInvoiceNumberSerializer,
    InvoiceSerializer,
    InvoiceTransactionSerializer,
)
from leaseslicensing.components.main.api import NoPaginationListMixin
from leaseslicensing.helpers import is_finance_officer

logger = logging.getLogger(__name__)


class InvoiceFilterBackend(DatatablesFilterBackend):
    def filter_queryset(self, request, queryset, view):
        approval_id = request.GET.get("approval_id", None)
        if approval_id:
            queryset = queryset.filter(approval_id=approval_id)

        filter_invoice_organisation = (
            request.GET.get("filter_invoice_organisation")
            if request.GET.get("filter_invoice_organisation") != "all"
            else ""
        )
        filter_invoice_status = (
            request.GET.get("filter_invoice_status")
            if request.GET.get("filter_invoice_status") != "all"
            else ""
        )
        filter_invoice_due_date_from = request.GET.get("filter_invoice_due_date_from")
        filter_invoice_due_date_to = request.GET.get("filter_invoice_due_date_to")

        if filter_invoice_organisation:
            queryset = queryset.filter(
                approval__current_proposal__org_applicant=filter_invoice_organisation
            )

        if filter_invoice_status:
            if "overdue" == filter_invoice_status:
                queryset = queryset.filter(
                    status=Invoice.INVOICE_STATUS_UNPAID,
                    date_due__lte=datetime.now().date(),
                )
            else:
                queryset = queryset.filter(status=filter_invoice_status)

        if filter_invoice_due_date_from:
            filter_invoice_due_date_from = datetime.strptime(
                filter_invoice_due_date_from, "%Y-%m-%d"
            )
            queryset = queryset.filter(date_due__gte=filter_invoice_due_date_from)

        if filter_invoice_due_date_to:
            filter_invoice_due_date_to = datetime.strptime(
                filter_invoice_due_date_to, "%Y-%m-%d"
            )
            queryset = queryset.filter(date_due__lte=filter_invoice_due_date_to)

        return queryset


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    filter_backends = [InvoiceFilterBackend]

    @action(detail=False, methods=["get"])
    def statuses(self, request, *args, **kwargs):
        return Response(
            [
                {"id": status[0], "name": status[1]}
                for status in Invoice.INVOICE_STATUS_CHOICES
            ]
        )

    @action(detail=True, methods=["get"])
    def transactions(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = InvoiceTransactionSerializer(
            instance.transactions.all(), many=True
        )
        return Response(serializer.data)

    @action(detail=True, methods=["POST"])
    def record_transaction(self, request, *args, **kwargs):
        if not is_finance_officer(request):
            return Response(
                {
                    "message": "You do not have permission to record an invoice transaction"
                }
            )

        instance = self.get_object()

        credit = request.data.get("credit", Decimal("0.00"))
        debit = request.data.get("debit", Decimal("0.00"))

        serializer = InvoiceTransactionSerializer(
            data={
                "invoice": instance.id,
                "credit": credit,
                "debit": debit,
            }
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        invoice_transaction = serializer.save()

        if Decimal("0.00") == invoice_transaction.invoice.balance:
            invoice_transaction.invoice.status = Invoice.INVOICE_STATUS_PAID
            invoice_transaction.invoice.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=["PATCH"])
    def edit_oracle_invoice_number(self, request, *args, **kwargs):
        if not is_finance_officer(request):
            return Response(
                {
                    "message": "You do not have permission to edit an Oracle Invoice Number"
                }
            )

        instance = self.get_object()
        logger.debug(instance.__dict__)
        oracle_invoice_number = request.data.get("oracle_invoice_number", None)
        if not oracle_invoice_number:
            return Response({"message": "Oracle Invoice Number is required"})

        serializer = InvoiceEditOracleInvoiceNumberSerializer(
            instance, data={"oracle_invoice_number": oracle_invoice_number}
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        serializer.save()

        return Response(serializer.data)


class InvoiceTransactionViewSet(viewsets.ModelViewSet):
    queryset = InvoiceTransaction.objects.all()
    serializer_class = InvoiceTransactionSerializer


class CPICalculationMethodViewSet(
    mixins.ListModelMixin, viewsets.GenericViewSet, NoPaginationListMixin
):
    queryset = CPICalculationMethod.objects.all()
    serializer_class = CPICalculationMethodSerializer


class PayInvoiceSuccessCallbackView(APIView):
    throttle_classes = [AnonRateThrottle]

    def get(self, request, uuid, format=None):
        logger.info("Leases Licensing Pay Invoice Success View get method called.")

        if (
            uuid
            and Invoice.objects.filter(
                uuid=uuid, processing_status=Invoice.UNPAID
            ).exists()
        ):
            logger.info(
                f"Invoice uuid: {uuid}.",
            )
            invoice = Invoice.objects.get(uuid=uuid)
            invoice.processing_status = Invoice.PAID
            invoice.save()

            logger.info(
                "Returning status.HTTP_200_OK. Invoice marked as paid successfully.",
            )
            # this end-point is called by an unmonitored get request in ledger so there is no point having a
            # a response body however we will return a status in case this is used on the ledger end in future
            return Response(status=status.HTTP_200_OK)

        # If there is no uuid to identify the cart then send a bad request status back in case ledger can
        # do something with this in future
        logger.info(
            "Returning status.HTTP_400_BAD_REQUEST bad request as there "
            f"was not an unpaid invoice with uuid: {uuid}."
        )
        return Response(status=status.HTTP_400_BAD_REQUEST)
