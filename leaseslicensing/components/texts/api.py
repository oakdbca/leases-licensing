import logging

from rest_framework import viewsets

from leaseslicensing.components.main.api import KeyValueListMixin
from leaseslicensing.components.texts.models import DetailsText
from leaseslicensing.components.texts.serializers import DetailsTextSerializer
from leaseslicensing.permissions import IsAssessor

logger = logging.getLogger(__name__)


class DetailsTextViewSet(
    viewsets.ModelViewSet,
    KeyValueListMixin,
):
    model = DetailsText
    serializer_class = DetailsTextSerializer
    key_value_display_field = "target"
    key_value_serializer_class = DetailsTextSerializer
    queryset = DetailsText.objects.all()
    permission_classes = [IsAssessor]
