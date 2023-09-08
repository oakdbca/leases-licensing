from rest_framework import serializers

from leaseslicensing.components.texts.models import DetailsText


class DetailsTextSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetailsText
        fields = ["target", "body"]
