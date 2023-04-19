import logging

from rest_framework import viewsets

from leaseslicensing.components.main.api import KeyValueListMixin
from leaseslicensing.components.tenure.models import LGA, Category, District, Region
from leaseslicensing.components.tenure.serializers import (
    CategorySerializer,
    DistrictKeyValueSerializer,
    DistrictSerializer,
    LGASerializer,
    RegionSerializer,
)

logger = logging.getLogger(__name__)


class RegionViewSet(viewsets.ModelViewSet, KeyValueListMixin):
    model = Region
    serializer_class = RegionSerializer
    key_value_display_field = "name"

    def get_queryset(self):
        return Region.objects.all()


class DistrictViewSet(viewsets.ModelViewSet, KeyValueListMixin):
    model = District
    serializer_class = DistrictSerializer
    key_value_display_field = "name"

    def get_queryset(self):
        return District.objects.all()

    def get_serializer_class(self):
        if "key_value_list" == self.action:
            return DistrictKeyValueSerializer
        return super().get_serializer_class()


class LGAViewSet(viewsets.ModelViewSet, KeyValueListMixin):
    model = LGA
    serializer_class = LGASerializer
    key_value_display_field = "name"

    def get_queryset(self):
        return LGA.objects.all()


class CategoryViewSet(viewsets.ModelViewSet, KeyValueListMixin):
    model = Category
    serializer_class = CategorySerializer
    key_value_display_field = "name"

    def get_queryset(self):
        return Category.objects.all()
