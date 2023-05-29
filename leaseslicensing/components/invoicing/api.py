import logging
from datetime import datetime
from decimal import Decimal

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_datatables.filters import DatatablesFilterBackend

from leaseslicensing.components.invoicing.models import Invoice, InvoiceTransaction
from leaseslicensing.components.invoicing.serializers import (
    InvoiceEditOracleInvoiceNumberSerializer,
    InvoiceSerializer,
    InvoiceTransactionSerializer,
)
from leaseslicensing.helpers import is_finance_officer

logger = logging.getLogger(__name__)


class InvoiceFilterBackend(DatatablesFilterBackend):
    def filter_queryset(self, request, queryset, view):
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
