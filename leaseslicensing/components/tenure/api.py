import logging

from rest_framework import viewsets

from leaseslicensing.components.main.api import KeyValueListMixin, NoPaginationListMixin
from leaseslicensing.components.tenure.models import LGA, District, Group, Region
from leaseslicensing.components.tenure.serializers import (
    DistrictKeyValueSerializer,
    DistrictSerializer,
    GroupSerializer,
    LGASerializer,
    RegionSerializer,
)

logger = logging.getLogger(__name__)


class RegionViewSet(viewsets.ModelViewSet, KeyValueListMixin, NoPaginationListMixin):
    model = Region
    serializer_class = RegionSerializer
    key_value_display_field = "name"
    key_value_serializer_class = RegionSerializer
    queryset = Region.objects.all()


class DistrictViewSet(viewsets.ModelViewSet, KeyValueListMixin, NoPaginationListMixin):
    model = District
    serializer_class = DistrictSerializer
    key_value_serializer_class = DistrictKeyValueSerializer
    key_value_display_field = "name"
    queryset = District.objects.all()


class LGAViewSet(viewsets.ModelViewSet, KeyValueListMixin, NoPaginationListMixin):
    model = LGA
    serializer_class = LGASerializer
    key_value_display_field = "name"
    key_value_serializer_class = LGASerializer
    queryset = LGA.objects.all()


class GroupViewSet(viewsets.ModelViewSet, KeyValueListMixin, NoPaginationListMixin):
    model = Group
    serializer_class = GroupSerializer
    key_value_display_field = "name"
    key_value_serializer_class = GroupSerializer
    queryset = Group.objects.all()
