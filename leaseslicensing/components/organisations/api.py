import logging
import traceback

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import CharField, IntegerField, Q, Value
from django.db.models.functions import Concat
from ledger_api_client.ledger_models import EmailUserRO as EmailUser
from ledger_api_client.managed_models import SystemGroupPermission
from rest_framework import serializers, status, views, viewsets
from rest_framework.decorators import action as list_route
from rest_framework.decorators import renderer_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework_datatables.pagination import DatatablesPageNumberPagination
from ledger_api_client.utils import update_organisation_obj

from leaseslicensing.components.main.api import (
    KeyValueListMixin,
    UserActionLoggingViewset,
)
from leaseslicensing.components.main.decorators import (
    basic_exception_handler,
    logging_action,
)
from leaseslicensing.components.main.filters import LedgerDatatablesFilterBackend
from leaseslicensing.components.organisations.models import (  # ledger_organisation,
    Organisation,
    OrganisationContact,
    OrganisationRequest,
    OrganisationRequestUserAction,
)
from leaseslicensing.components.organisations.serializers import (
    MyOrganisationsSerializer,
    OrganisationActionSerializer,
    OrganisationCheckExistSerializer,
    OrganisationCheckSerializer,
    OrganisationCommsSerializer,
    OrganisationContactAdminCountSerializer,
    OrganisationContactSerializer,
    OrganisationKeyValueSerializer,
    OrganisationLogEntrySerializer,
    OrganisationPinCheckSerializer,
    OrganisationRequestActionSerializer,
    OrganisationRequestCommsSerializer,
    OrganisationRequestDTSerializer,
    OrganisationRequestLogEntrySerializer,
    OrganisationRequestSerializer,
    OrganisationSerializer,
    OrgUserAcceptSerializer,
)
from leaseslicensing.components.proposals.api import ProposalRenderer
from leaseslicensing.helpers import is_customer, is_internal

logger = logging.getLogger(__name__)


class OrganisationViewSet(UserActionLoggingViewset, KeyValueListMixin):
    queryset = Organisation.objects.none()
    serializer_class = OrganisationSerializer
    key_value_display_field = "ledger_organisation_name"
    key_value_serializer_class = OrganisationKeyValueSerializer

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return Organisation.objects.all()
        elif is_customer(self.request):
            if "organisation_lookup" == self.action:
                # Allow customers access to organisation lookup
                return Organisation.objects.only(
                    "id", "ledger_organisation_name", "ledger_organisation_abn"
                )
            if "validate_pins" == self.action:
                return Organisation.objects.all()
            logger.info(list(Organisation.objects.filter(delegates__user=user.id)))
            return Organisation.objects.filter(delegates__user=user.id)
        return Organisation.objects.none()

    @list_route(
        methods=[
            "GET",
        ],
        detail=False,
    )
    def organisation_lookup(self, request, *args, **kwargs):
        search_term = request.GET.get("term", "")
        organisations = self.get_queryset().annotate(
            search_term=Concat(
                "ledger_organisation_name",
                Value(" "),
                "ledger_organisation_abn",
                output_field=CharField(),
            )
        )
        organisations = organisations.filter(search_term__icontains=search_term).only(
            "id", "ledger_organisation_name", "ledger_organisation_abn"
        )[:10]
        data_transform = [
            {
                "id": organisation.id,
                "text": f"{organisation.ledger_organisation_name} (ABN: {organisation.ledger_organisation_abn})",
                "first_five": organisation.first_five,
            }
            for organisation in organisations
        ]
        return Response({"results": data_transform})

    @logging_action(
        methods=[
            "GET",
        ],
        detail=True,
    )
    @basic_exception_handler
    def contacts(self, request, *args, **kwargs):
        instance = self.get_object()
        admin_count = instance.contacts.filter(user_role="organisation_admin").count()
        logger.debug("admin_count = " + str(admin_count))
        queryset = instance.contacts.exclude(user_status="pending")
        queryset = queryset.annotate(
            admin_count=Value(admin_count, output_field=IntegerField())
        )
        serializer = OrganisationContactAdminCountSerializer(queryset, many=True)
        return Response(serializer.data)

    @logging_action(
        methods=[
            "GET",
        ],
        detail=True,
    )
    @basic_exception_handler
    def contacts_linked(self, request, *args, **kwargs):
        qs = self.get_queryset()
        serializer = OrganisationContactSerializer(qs, many=True)
        return Response(serializer.data)

    @logging_action(
        methods=[
            "GET",
        ],
        detail=True,
    )
    @basic_exception_handler
    def contacts_exclude(self, request, *args, **kwargs):
        instance = self.get_object()
        qs = instance.contacts.exclude(user_status="draft")
        serializer = OrganisationContactSerializer(qs, many=True)
        return Response(serializer.data)

    @logging_action(
        methods=[
            "POST",
        ],
        detail=True,
    )
    @basic_exception_handler
    def validate_pins(self, request, *args, **kwargs):
        instance = self.get_object()
        logger.debug("request.data = " + str(request.data))
        serializer = OrganisationPinCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ret = instance.validate_pins(
            serializer.validated_data["pin1"],
            serializer.validated_data["pin2"],
            request,
        )

        if ret is None:
            # user has already been to this organisation - don't add again
            return Response({"valid": "User already exists"})

        data = {"valid": ret}
        if data["valid"]:
            # Notify each Admin member of request.
            instance.send_organisation_request_link_notification(request)
        return Response(data)

    @logging_action(
        methods=[
            "POST",
        ],
        detail=True,
    )
    @basic_exception_handler
    def accept_user(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = OrgUserAcceptSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_obj = EmailUser.objects.get(
            email=serializer.validated_data["email"].lower()
        )
        instance.accept_user(user_obj, request)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @logging_action(
        methods=[
            "POST",
        ],
        detail=True,
    )
    @basic_exception_handler
    def accept_declined_user(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = OrgUserAcceptSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_obj = EmailUser.objects.get(
            email=serializer.validated_data["email"].lower()
        )
        instance.accept_declined_user(user_obj, request)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @logging_action(
        methods=[
            "POST",
        ],
        detail=True,
    )
    @basic_exception_handler
    def decline_user(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = OrgUserAcceptSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_obj = EmailUser.objects.get(
            email=serializer.validated_data["email"].lower()
        )
        instance.decline_user(user_obj, request)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @logging_action(
        methods=[
            "POST",
        ],
        detail=True,
    )
    @basic_exception_handler
    def unlink_user(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = OrgUserAcceptSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_obj = EmailUser.objects.get(
            email=serializer.validated_data["email"].lower()
        )
        instance.unlink_user(user_obj, request)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @logging_action(
        methods=[
            "POST",
        ],
        detail=True,
    )
    @basic_exception_handler
    def make_admin_user(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = OrgUserAcceptSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_obj = EmailUser.objects.get(
            email=serializer.validated_data["email"].lower()
        )
        instance.make_admin_user(user_obj, request)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @logging_action(
        methods=[
            "POST",
        ],
        detail=True,
    )
    @basic_exception_handler
    def make_user(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = OrgUserAcceptSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_obj = EmailUser.objects.get(
            email=serializer.validated_data["email"].lower()
        )
        instance.make_user(user_obj, request)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @logging_action(
        methods=[
            "POST",
        ],
        detail=True,
    )
    @basic_exception_handler
    def make_consultant(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = OrgUserAcceptSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_obj = EmailUser.objects.get(
            email=serializer.validated_data["email"].lower()
        )
        instance.make_consultant(user_obj, request)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @logging_action(
        methods=[
            "POST",
        ],
        detail=True,
    )
    @basic_exception_handler
    def suspend_user(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = OrgUserAcceptSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_obj = EmailUser.objects.get(
            email=serializer.validated_data["email"].lower()
        )
        instance.suspend_user(user_obj, request)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @logging_action(
        methods=[
            "POST",
        ],
        detail=True,
    )
    @basic_exception_handler
    def reinstate_user(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = OrgUserAcceptSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_obj = EmailUser.objects.get(
            email=serializer.validated_data["email"].lower()
        )
        instance.reinstate_user(user_obj, request)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @logging_action(
        methods=[
            "POST",
        ],
        detail=True,
    )
    @basic_exception_handler
    def relink_user(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = OrgUserAcceptSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_obj = EmailUser.objects.get(
            email=serializer.validated_data["email"].lower()
        )
        instance.relink_user(user_obj, request)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @logging_action(
        methods=[
            "GET",
        ],
        detail=True,
    )
    @basic_exception_handler
    def action_log(self, request, *args, **kwargs):
        instance = self.get_object()
        qs = instance.action_logs.all()
        serializer = OrganisationActionSerializer(qs, many=True)
        return Response(serializer.data)

    @logging_action(
        methods=[
            "GET",
        ],
        detail=True,
    )
    @basic_exception_handler
    def comms_log(self, request, *args, **kwargs):
        instance = self.get_object()
        qs = instance.comms_logs.all()
        serializer = OrganisationCommsSerializer(qs, many=True)
        return Response(serializer.data)

    @logging_action(
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
            request.data["organisation"] = f"{instance.id}"
            request.data["staff"] = f"{request.user.id}"
            request.data._mutable = mutable
            serializer = OrganisationLogEntrySerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            comms = serializer.save()

            # Save the files
            for f in request.FILES.getlist("files"):
                document = comms.documents.create()
                document.name = str(f)
                document._file = f
                document.save()

            return Response(serializer.data)

    @list_route(
        methods=[
            "POST",
        ],
        detail=False,
    )
    @basic_exception_handler
    def existence(self, request, *args, **kwargs):
        serializer = OrganisationCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = Organisation.existence(serializer.validated_data["abn"])
        # Check request user cannot be relinked to org.
        data.update([("user", request.user.id)])
        data.update([("abn", request.data["abn"])])
        serializer = OrganisationCheckExistSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)

    # Todo: Implement for segregatted system
    # @logging_action(
    #     methods=[
    #         "POST",
    #     ],
    #     detail=True,
    # )
    # @basic_exception_handler
    # def update_details(self, request, *args, **kwargs):
    #     org = self.get_object()
    #     instance = org.organisation
    #     data = request.data
    #     serializer = DetailsSerializer(
    #         instance, data=data, context={"request": request}
    #     )
    #     serializer.is_valid(raise_exception=True)
    #     instance = serializer.save()
    #     # serializer = self.get_serializer(org)

    #     if is_internal(request) and "apply_application_discount" in request.data:
    #         data = request.data
    #         if not data["apply_application_discount"]:
    #             data["application_discount"] = 0
    #         if not data["apply_licence_discount"]:
    #             data["licence_discount"] = 0

    #         if data["application_discount"] == 0:
    #             data["apply_application_discount"] = False
    #         if data["licence_discount"] == 0:
    #             data["apply_licence_discount"] = False

    #         if (
    #             is_internal(request)
    #             and "charge_once_per_year" in request.data
    #             and request.data.get("charge_once_per_year")
    #         ):
    #             DD = int(request.data.get("charge_once_per_year").split("/")[0])
    #             MM = int(request.data.get("charge_once_per_year").split("/")[1])
    #             YYYY = timezone.now().year  # set to current year
    #             data["charge_once_per_year"] = f"{YYYY}-{MM}-{DD}"
    #         else:
    #             data["charge_once_per_year"] = None

    #         serializer = SaveDiscountSerializer(org, data=data)
    #         serializer.is_valid(raise_exception=True)
    #         instance = serializer.save()

    #     serializer = self.get_serializer(org)
    #     return Response(serializer.data)

    @logging_action(methods=['POST',], detail=True)
    def update_address(self, request, *args, **kwargs):
           try:
                   org = self.get_object()
                #    print("org_got: {}".format(org.__dict__))
                #    print("org_id: {}".format(org.ledger_organisation_id))
                #    print("org_name: {}".format(org.ledger_organisation_name))
                #    print("org_abn: {}".format(org.ledger_organisation_abn))
                #    print("org_email: {}".format(org.ledger_organisation_email))
                   #org_obj = Organisation.objects.get(id=org.id)
                #    print("OBJECT: {}".format(request.data))
                   response_from_ledger = update_organisation_obj(request.data)
                   print("RESPONSE_LEDGER: {}".format(response_from_ledger))
                   #data = request.data
                   #print("org_tname: {}".format(org.trading_name))
                #    instance = org.organisation
                #    serializer = OrganisationAddressSerializer(data=request.data)
                #    serializer.is_valid(raise_exception=True)
                #    address, created = OrganisationAddress.objects.get_or_create(
                #            line1 = serializer.validated_data['line1'],
                #            locality = serializer.validated_data['locality'],
                #            state = serializer.validated_data['state'],
                #            country = serializer.validated_data['country'],
                #            postcode = serializer.validated_data['postcode'],
                #            organisation = instance
                #    )
                #    instance.postal_address = address
                #    instance.save()
                #    #send_organisation_address_updated_email_notification(request.user, instance, org, request)
                #    serializer = self.get_serializer(org)
                   #return Response(serializer.data);
                   return response_from_ledger
           except serializers.ValidationError:
                   print(traceback.print_exc())
                   raise
           except ValidationError as e:
                   print(traceback.print_exc())
                   raise serializers.ValidationError(repr(e.error_dict))
           except Exception as e:
                   print(traceback.print_exc())
                   raise serializers.ValidationError(str(e))

    @logging_action(
        methods=[
            "POST",
        ],
        detail=True,
    )
    @basic_exception_handler
    def upload_id(self, request, *args, **kwargs):
        pass


# from rest_framework import filters
# class OrganisationListFilterView(generics.ListAPIView):
#        """ https://cop-internal.dbca.wa.gov.au/api/filtered_organisations?search=Org1
#        """
#        #queryset = Organisation.objects.all()
#        queryset = ledger_organisation.objects.none()
#        serializer_class = LedgerOrganisationFilterSerializer
#        filter_backends = (filters.SearchFilter,)
#        search_fields = ('name', 'trading_name',)
#
#        def get_queryset(self):
#                org_list = Organisation.objects.all().values_list('organisation_id', flat=True)
#                return ledger_organisation.objects.filter(id__in=org_list)


class OrganisationRequestFilterBackend(LedgerDatatablesFilterBackend):
    """
    Custom filters
    """

    def filter_queryset(self, request, queryset, view):
        total_count = queryset.count()

        filter_organisation = request.GET.get("filter_organisation", None)
        filter_role = request.GET.get("filter_role", None)
        filter_status = request.GET.get("filter_status", None)

        if filter_organisation:
            logger.debug("filter_organisation: %s", filter_organisation)
            filter_organisation = int(filter_organisation)
            queryset = queryset.filter(organisation_id=filter_organisation)

        if filter_role:
            queryset = queryset.filter(role=filter_role)

        if filter_status:
            queryset = queryset.filter(status=filter_status)

        queryset = self.apply_request(
            request, queryset, view, ledger_lookup_fields=["ind_applicant"]
        )

        setattr(view, "_datatables_total_count", total_count)
        return queryset


class OrganisationRequestPaginatedViewSet(viewsets.ModelViewSet):
    filter_backends = (OrganisationRequestFilterBackend,)
    pagination_class = DatatablesPageNumberPagination
    renderer_classes = (ProposalRenderer,)
    page_size = 10
    queryset = OrganisationRequest.objects.all()
    serializer_class = OrganisationRequestSerializer


class OrganisationRequestsViewSet(UserActionLoggingViewset):
    queryset = OrganisationRequest.objects.all()
    serializer_class = OrganisationRequestSerializer

    def get_serializer_class(self):
        if "retrieve" == self.action:
            return OrganisationRequestDTSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        if is_internal(self.request):
            return OrganisationRequest.objects.all()
        elif is_customer(self.request):
            return OrganisationRequest.objects.filter(
                requester=self.request.user.id
            ).exclude(status="declined")
        return OrganisationRequest.objects.none()

    @list_route(
        methods=[
            "GET",
        ],
        detail=False,
    )
    def datatable_list(self, request, *args, **kwargs):
        try:
            qs = self.get_queryset()
            serializer = OrganisationRequestDTSerializer(qs, many=True)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    # @list_route(methods=['GET',])
    # def user_organisation_request_list(self, request, *args, **kwargs):
    #     try:
    #         queryset = self.get_queryset()
    #         queryset = queryset.filter(requester = request.user)

    #         # instance = OrganisationRequest.objects.get(requester = request.user)
    #         serializer = self.get_serializer(queryset, many=True)
    #         return Response(serializer.data)
    #     except serializers.ValidationError:
    #         print(traceback.print_exc())
    #         raise
    #     except ValidationError as e:
    #         print(traceback.print_exc())
    #         raise serializers.ValidationError(repr(e.error_dict))
    #     except Exception as e:
    #         print(traceback.print_exc())
    #         raise serializers.ValidationError(str(e))

    @list_route(
        methods=[
            "GET",
        ],
        detail=False,
    )
    def get_pending_requests(self, request, *args, **kwargs):
        try:
            qs = self.get_queryset().filter(
                requester=request.user, status="with_assessor"
            )
            serializer = OrganisationRequestDTSerializer(qs, many=True)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @list_route(
        methods=[
            "GET",
        ],
        detail=False,
    )
    def get_amendment_requested_requests(self, request, *args, **kwargs):
        try:
            qs = self.get_queryset().filter(
                requester=request.user, status="amendment_requested"
            )
            serializer = OrganisationRequestDTSerializer(qs, many=True)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @logging_action(
        methods=[
            "GET",
        ],
        detail=True,
    )
    def assign_request_user(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.assign_to(request.user.id, request)
            serializer = OrganisationRequestDTSerializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @logging_action(
        methods=[
            "PATCH",
        ],
        detail=True,
    )
    def assign_user(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            user_id = request.data.get("user_id")
            logger.info("user_id: %s", user_id)
            instance.assign_to(user_id, request)
            serializer = OrganisationRequestDTSerializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @logging_action(
        methods=[
            "PATCH",
        ],
        detail=True,
    )
    def unassign(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.unassign(request)
            serializer = OrganisationRequestDTSerializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @logging_action(
        methods=[
            "PATCH",
        ],
        detail=True,
    )
    def accept(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.accept(request)
            serializer = OrganisationRequestDTSerializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            # print(traceback.print_exc())
            # raise serializers.ValidationError(repr(e.error_dict))
            if hasattr(e, "error_dict"):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                if hasattr(e, "message"):
                    raise serializers.ValidationError(e.message)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @logging_action(
        methods=[
            "GET",
        ],
        detail=True,
    )
    def amendment_request(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.amendment_request(request)
            serializer = OrganisationRequestSerializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @logging_action(
        methods=[
            "PUT",
        ],
        detail=True,
    )
    def reupload_identification_amendment_request(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.reupload_identification_amendment_request(request)
            serializer = OrganisationRequestSerializer(instance, partial=True)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @logging_action(
        methods=[
            "PATCH",
        ],
        detail=True,
    )
    def decline(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            reason = ""
            instance.decline(reason, request)
            serializer = OrganisationRequestDTSerializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @logging_action(
        methods=[
            "POST",
        ],
        detail=True,
    )
    def assign_to(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            user_id = request.data.get("user_id", None)
            user = None
            if not user_id:
                raise serializers.ValiationError("A user id is required")
            try:
                user = EmailUser.objects.get(id=user_id)
            except EmailUser.DoesNotExist:
                raise serializers.ValidationError(
                    "A user with the id passed in does not exist"
                )
            instance.assign_to(user, request)
            serializer = OrganisationRequestSerializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @logging_action(
        methods=[
            "GET",
        ],
        detail=True,
    )
    def action_log(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            qs = instance.action_logs.all()
            serializer = OrganisationRequestActionSerializer(qs, many=True)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @logging_action(
        methods=[
            "GET",
        ],
        detail=True,
    )
    def comms_log(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            qs = instance.comms_logs.all()
            serializer = OrganisationRequestCommsSerializer(qs, many=True)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @logging_action(
        methods=[
            "POST",
        ],
        detail=True,
    )
    @renderer_classes((JSONRenderer,))
    def add_comms_log(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                instance = self.get_object()
                mutable = request.data._mutable
                request.data._mutable = True
                request.data["organisation"] = f"{instance.id}"
                request.data["request"] = f"{instance.id}"
                request.data["staff"] = f"{request.user.id}"
                request.data._mutable = mutable
                serializer = OrganisationRequestLogEntrySerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                comms = serializer.save()

                # Save the files
                for f in request.FILES.getlist("files"):
                    document = comms.documents.create()
                    document.name = str(f)
                    document._file = f
                    document.save()

                return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.validated_data["requester"] = request.user.id
            if request.data["role"] == "consultant":
                # Check if consultant can be relinked to org.
                data = Organisation.existence(request.data["abn"])
                data.update([("user", request.user.id)])
                data.update([("abn", request.data["abn"])])
                existing_org = OrganisationCheckExistSerializer(data=data)
                existing_org.is_valid(raise_exception=True)
            with transaction.atomic():
                instance = serializer.save()
                instance.log_user_action(
                    OrganisationRequestUserAction.ACTION_LODGE_REQUEST.format(
                        instance.id
                    ),
                    request,
                )
                instance.send_organisation_request_email_notification(request)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))


class OrganisationAccessGroupMembers(views.APIView):
    renderer_classes = [
        JSONRenderer,
    ]

    def get(self, request, format=None):
        if not is_internal(request):
            raise PermissionDenied()

        members = []
        permissions = SystemGroupPermission.objects.filter(
            system_group__name=settings.GROUP_NAME_ORGANISATION_ACCESS
        )
        for permission in permissions:
            members.append(
                {
                    "name": permission.emailuser.get_full_name(),
                    "id": permission.emailuser.id,
                }
            )

        return Response(members)


class OrganisationContactViewSet(viewsets.ModelViewSet):
    serializer_class = OrganisationContactSerializer
    queryset = OrganisationContact.objects.all()

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return OrganisationContact.objects.all()
        elif is_customer(self.request):
            user_orgs = [org.id for org in user.leaseslicensing_organisations.all()]
            return OrganisationContact.objects.filter(Q(organisation_id__in=user_orgs))
        return OrganisationContact.objects.none()

    def destroy(self, request, *args, **kwargs):
        """delete an Organisation contact"""
        num_admins = (
            self.get_object()
            .organisation.contacts.filter(user_role="organisation_admin")
            .count()
        )
        org_contact = self.get_object().organisation.contacts.get(id=kwargs["pk"])
        if num_admins == 1 and org_contact.user_role == "organisation_admin":
            raise serializers.ValidationError(
                "Cannot delete the last Organisation Admin"
            )
        return super().destroy(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if "contact_form" in request.data.get("user_status"):
            serializer.save(user_status="contact_form")
        else:
            serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MyOrganisationsViewSet(viewsets.ModelViewSet):
    queryset = Organisation.objects.all()
    serializer_class = MyOrganisationsSerializer

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return Organisation.objects.all()
        elif is_customer(self.request):
            return Organisation.objects.filter(
                contacts__user=user.id,
                contacts__user_status="active",
                contacts__user_role="organisation_admin",
            )
        return Organisation.objects.none()
