import logging

from django.db import transaction
from rest_framework import viewsets
from rest_framework.decorators import action as detail_route
from rest_framework.decorators import action as list_route
from rest_framework.decorators import renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

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

logger = logging.getLogger("payment_checkout")


class GlobalSettingsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = GlobalSettings.objects.all().order_by("id")
    serializer_class = GlobalSettingsSerializer


class RequiredDocumentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RequiredDocument.objects.all()
    serializer_class = RequiredDocumentSerializer

    # def get_queryset(self):
    #     categories=ActivityCategory.objects.filter(activity_type='marine')
    #     return categories


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


class ApplicationTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ApplicationType.objects.all()
    serializer_class = ApplicationTypeSerializer

    @list_route(methods=["GET"], detail=False)
    def key_value_list(self, request, *args, **kwargs):
        queryset = self.get_queryset().only("id", "name")
        self.serializer_class = ApplicationTypeKeyValueSerializer
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # class PaymentViewSet(viewsets.ModelViewSet):
    #    #queryset = Proposal.objects.all()
    #    queryset = Proposal.objects.none()
    #    #serializer_class = ProposalSerializer
    #    serializer_class = ProposalSerializer
    #    lookup_field = 'id'
    #
    #    def create(self, request, *args, **kwargs):
    #        response = super(PaymentViewSet, self).create(request, *args, **kwargs)
    #        # here may be placed additional operations for
    #        # extracting id of the object and using reverse()
    #        fallback_url = request.build_absolute_uri('/')
    #        return HttpResponseRedirect(redirect_to=fallback_url + '/success/')
    #
    #
    # class BookingSettlementReportView(views.APIView):
    #    renderer_classes = (JSONRenderer,)
    #
    #    def get(self,request,format=None):
    #        try:
    #            http_status = status.HTTP_200_OK
    #            #parse and validate data
    #            report = None
    #            data = {
    #                "date":request.GET.get('date'),
    #            }
    #            serializer = BookingSettlementReportSerializer(data=data)
    #            serializer.is_valid(raise_exception=True)
    #            filename = 'Booking Settlement Report-{}'.format(str(serializer.validated_data['date']))
    #            # Generate Report
    #            report = reports.booking_bpoint_settlement_report(serializer.validated_data['date'])
    #            if report:
    #                response = HttpResponse(FileWrapper(report), content_type='text/csv')
    #                response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(filename)
    #                return response
    #            else:
    #                raise serializers.ValidationError('No report was generated.')
    #        except serializers.ValidationError:
    #            raise
    #        except Exception as e:
    #            traceback.print_exc()
    #
    #
    # class OracleJob(views.APIView):
    #    renderer_classes = [JSONRenderer,]
    #    def get(self, request, format=None):
    #        try:
    #            data = {
    #                "date":request.GET.get("date"),
    #                "override": request.GET.get("override")
    #            }
    #            serializer = OracleSerializer(data=data)
    #            serializer.is_valid(raise_exception=True)
    #            oracle_integration(serializer.validated_data['date'].strftime('%Y-%m-%d'),serializer.validated_data['override'])
    #            data = {'successful':True}
    #            return Response(data)
    #        except serializers.ValidationError:
    #            print(traceback.print_exc())
    #            raise
    #        except ValidationError as e:
    #            raise serializers.ValidationError(repr(e.error_dict))
    # if hasattr(e, 'error_dict') else serializers.ValidationError(e)
    #        except Exception as e:
    #            print(traceback.print_exc())
    #            raise serializers.ValidationError(str(e[0]))
