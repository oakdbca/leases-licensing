import logging

from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.db.models import CharField, Q, Value
from django.db.models.functions import Concat
from django_countries import countries
from ledger_api_client.api import get_account_details
from ledger_api_client.ledger_models import Address
from ledger_api_client.ledger_models import EmailUserRO as EmailUser  # EmailUserAction
from rest_framework import filters, generics, views
from rest_framework.decorators import action
from rest_framework.decorators import action as detail_route
from rest_framework.decorators import action as list_route
from rest_framework.decorators import renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from leaseslicensing.components.invoicing.models import ChargeMethod, RepetitionType
from leaseslicensing.components.invoicing.serializers import (
    ChargeMethodSerializer,
    RepetitionTypeSerializer,
)
from leaseslicensing.components.main.api import UserActionLoggingViewset
from leaseslicensing.components.main.decorators import basic_exception_handler
from leaseslicensing.components.main.serializers import (
    EmailUserSerializer,
    LimitedEmailUserSerializer,
)
from leaseslicensing.components.organisations.serializers import (
    OrganisationRequestDTSerializer,
)
from leaseslicensing.components.proposals.models import (
    Proposal,
    ProposalApplicant,
    Referral,
)
from leaseslicensing.components.users.models import EmailUserAction, EmailUserLogEntry
from leaseslicensing.components.users.serializers import (
    ContactSerializer,
    EmailUserActionSerializer,
    EmailUserLogEntrySerializer,
    PersonalSerializer,
    ProposalApplicantSerializer,
    UserAddressSerializer,
    UserFilterSerializer,
    UserSerializer,
)
from leaseslicensing.helpers import is_internal
from leaseslicensing.permissions import IsInternal

logger = logging.getLogger(__name__)


class GetChargeMethods(views.APIView):
    renderer_classes = [
        JSONRenderer,
    ]

    def get(self, request, format=None):
        charge_methods = ChargeMethod.objects.all()
        serializer = ChargeMethodSerializer(charge_methods, many=True)
        return Response(serializer.data)


class GetRepetitionTypes(views.APIView):
    renderer_classes = [
        JSONRenderer,
    ]

    def get(self, request, format=None):
        repetition_types = RepetitionType.objects.all()
        serializer = RepetitionTypeSerializer(repetition_types, many=True)
        return Response(serializer.data)


class GetCountries(views.APIView):
    renderer_classes = [
        JSONRenderer,
    ]

    def get(self, request, format=None):
        country_list = cache.get(settings.CACHE_KEY_COUNTRY_LIST)
        if not country_list:
            country_list = []
            for country in list(countries):
                country_list.append({"name": country.name, "code": country.code})
            cache.set(
                settings.CACHE_KEY_COUNTRY_LIST,
                country_list,
                settings.LOV_CACHE_TIMEOUT,
            )

        return Response(country_list)


class GetRequestUserID(views.APIView):
    """Yes, this is a bit silly but for now the get_account_details from ledger_api_client doesn't return the
    request user id"""

    renderer_classes = [
        JSONRenderer,
    ]

    def get(self, request, format=None):
        if request.user.is_anonymous:
            return Response({"id": None, "is_internal": False})
        return Response({"id": request.user.id, "is_internal": is_internal(request)})


class GetLedgerAccount(views.APIView):
    renderer_classes = [
        JSONRenderer,
    ]

    def get(self, request, format=None):
        if request.user.is_anonymous:
            return Response({"error": "User is not logged in."})
        response = get_account_details(request, str(request.user.id))
        return response


class GetProposalApplicant(views.APIView):
    renderer_classes = [
        JSONRenderer,
    ]

    def get(self, request, proposal_pk, format=None):
        proposal = Proposal.objects.get(id=proposal_pk)
        try:
            proposal_applicant = ProposalApplicant.objects.get(proposal=proposal)
        except ProposalApplicant.DoesNotExist:
            raise ValidationError("No applicant found for this proposal.")

        serializer = ProposalApplicantSerializer(
            proposal_applicant, context={"request": request}
        )
        return Response(serializer.data)


class GetProfile(views.APIView):
    renderer_classes = [
        JSONRenderer,
    ]

    def get(self, request, format=None):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(serializer.data)


class UserListFilterView(generics.ListAPIView):
    """https://cop-internal.dbca.wa.gov.au/api/filtered_users?search=russell"""

    queryset = EmailUser.objects.all()
    serializer_class = UserFilterSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ("email", "first_name", "last_name")


class UserViewSet(UserActionLoggingViewset):
    queryset = EmailUser.objects.all()
    serializer_class = UserSerializer

    def get_serializer_class(self):
        if not is_internal(self.request):
            return LimitedEmailUserSerializer
        return super().get_serializer_class()

    @basic_exception_handler
    def list(self, request, *args, **kwargs):
        search_term = request.GET.get("term", "")
        queryset = self.queryset.filter(
            Q(first_name__icontains=search_term) | Q(last_name__icontains=search_term)
        )[:10]
        if not is_internal(request):
            serializer = LimitedEmailUserSerializer(queryset, many=True)
        else:
            serializer = EmailUserSerializer(queryset, many=True)
        return Response(serializer.data)

    @detail_route(
        methods=[
            "GET",
        ],
        detail=False,
    )
    @basic_exception_handler
    def request_user_account(self, request, *args, **kwargs):
        instance = EmailUser.objects.get(id=request.user.id)
        serializer = UserSerializer(instance, context={"request": request})
        return Response(serializer.data)

    @action(
        methods=[
            "GET",
        ],
        detail=False,
        permission_classes=[IsInternal],
    )
    def person_lookup(self, request, *args, **kwargs):
        search_term = request.GET.get("term", "")
        people = self.get_queryset().annotate(
            search_term=Concat(
                "first_name",
                Value(" "),
                "last_name",
                Value(" "),
                "email",
                output_field=CharField(),
            )
        )
        people = people.filter(search_term__icontains=search_term).values(
            "id", "email", "first_name", "last_name"
        )[:10]
        data_transform = [
            {
                "id": customer["id"],
                "text": customer["first_name"]
                + " "
                + customer["last_name"]
                + " ("
                + customer["email"]
                + ")",
            }
            for customer in people
        ]
        return Response({"results": data_transform})

    @list_route(
        methods=[
            "GET",
        ],
        detail=False,
        permission_classes=[IsInternal],
    )
    @basic_exception_handler
    def get_referees(self, request, *args, **kwargs):
        search_term = request.GET.get("term", "")

        # Allow for search of first name, last name and concatenation of both
        department_users = EmailUser.objects.annotate(
            search_term=Concat(
                "first_name",
                Value(" "),
                "last_name",
                Value(" "),
                "email",
                output_field=CharField(),
            )
        ).filter(is_staff=True)

        department_users = department_users.filter(
            search_term__icontains=search_term
        ).values("id", "email", "first_name", "last_name")[:10]
        external_referee_ids = list(
            Referral.objects.filter(is_external=True).values_list("referral", flat=True)
        )
        external_referees = EmailUser.objects.filter(
            id__in=external_referee_ids
        ).annotate(
            search_term=Concat(
                "first_name",
                Value(" "),
                "last_name",
                Value(" "),
                "email",
                output_field=CharField(),
            )
        )
        external_referees = external_referees.filter(
            search_term__icontains=search_term
        ).values("id", "email", "first_name", "last_name")[:10]

        internal = {
            "text": "Internal",
            "children": [
                {
                    "id": person["email"],
                    "text": f"{person['first_name']} {person['last_name']} ({person['email']})",
                }
                for person in department_users
            ],
        }
        external = {
            "text": "External ",
            "children": [
                {
                    "id": person["email"],
                    "text": f"{person['first_name']} {person['last_name']} ({person['email']})",
                }
                for person in external_referees
            ],
        }

        data_transform = []
        if department_users.exists():
            data_transform.append(internal)
        if external_referees.exists():
            data_transform.append(external)

        return Response({"results": data_transform})

    @list_route(
        methods=[
            "GET",
        ],
        detail=False,
        permission_classes=[IsInternal],
    )
    @basic_exception_handler
    def get_department_users(self, request, *args, **kwargs):
        search_term = request.GET.get("term", "")

        # Allow for search of first name, last name and concatenation of both
        department_users = EmailUser.objects.annotate(
            search_term=Concat(
                "first_name",
                Value(" "),
                "last_name",
                Value(" "),
                "email",
                output_field=CharField(),
            )
        ).filter(is_staff=True)

        department_users = department_users.filter(
            search_term__icontains=search_term
        ).values("id", "email", "first_name", "last_name")[:10]
        data_transform = [
            {
                "id": person["email"],
                "text": f"{person['first_name']} {person['last_name']} ({person['email']})",
            }
            for person in department_users
        ]

        return Response({"results": data_transform})

    @detail_route(
        methods=[
            "POST",
        ],
        detail=True,
    )
    @basic_exception_handler
    def update_personal(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = PersonalSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        serializer = UserSerializer(instance, context={"request": request})
        return Response(serializer.data)

    @detail_route(
        methods=[
            "POST",
        ],
        detail=True,
    )
    @basic_exception_handler
    def update_contact(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ContactSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        serializer = UserSerializer(instance, context={"request": request})
        return Response(serializer.data)

    @detail_route(
        methods=[
            "POST",
        ],
        detail=True,
    )
    @basic_exception_handler
    def update_address(self, request, *args, **kwargs):
        instance = self.get_object()
        # residential address
        residential_serializer = UserAddressSerializer(
            data=request.data.get("residential_address")
        )
        residential_serializer.is_valid(raise_exception=True)
        residential_address, created = Address.objects.get_or_create(
            line1=residential_serializer.validated_data["line1"],
            locality=residential_serializer.validated_data["locality"],
            state=residential_serializer.validated_data["state"],
            country=residential_serializer.validated_data["country"],
            postcode=residential_serializer.validated_data["postcode"],
            user=instance,
        )
        instance.residential_address = residential_address
        # postal address
        postal_address_data = request.data.get("postal_address")
        if request.data.get("postal_same_as_residential"):
            instance.postal_same_as_residential = True
            instance.postal_address = residential_address
        elif postal_address_data:
            postal_serializer = UserAddressSerializer(data=postal_address_data)
            postal_serializer.is_valid(raise_exception=True)
            postal_address, created = Address.objects.get_or_create(
                line1=postal_serializer.validated_data["line1"],
                locality=postal_serializer.validated_data["locality"],
                state=postal_serializer.validated_data["state"],
                country=postal_serializer.validated_data["country"],
                postcode=postal_serializer.validated_data["postcode"],
                user=instance,
            )
            instance.postal_address = postal_address
            instance.postal_same_as_residential = False

        instance.save()
        serializer = UserSerializer(instance, context={"request": request})
        return Response(serializer.data)

    @detail_route(
        methods=[
            "GET",
        ],
        detail=True,
    )
    @basic_exception_handler
    def pending_org_requests(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = OrganisationRequestDTSerializer(
            instance.organisationrequest_set.filter(status="with_assessor"),
            many=True,
            context={"request": request},
        )
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
        qs = EmailUserAction.objects.filter(email_user=instance.id)
        serializer = EmailUserActionSerializer(qs, many=True)
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
        qs = EmailUserLogEntry.objects.filter(email_user=instance.id)
        serializer = EmailUserLogEntrySerializer(qs, many=True)
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
            request.data["email_user"] = f"{instance.id}"
            request.data["staff"] = f"{request.user.id}"
            request.data._mutable = mutable
            serializer = EmailUserLogEntrySerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            comms = serializer.save()

            # Save the files
            for f in request.FILES.getlist("files"):
                document = comms.documents.create()
                document.name = str(f)
                document._file = f
                document.save()

            return Response(serializer.data)
