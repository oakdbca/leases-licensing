from rest_framework import serializers

from leaseslicensing.components.tenure.models import LGA, District, Group, Region


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = "__all__"


class DistrictSerializer(serializers.ModelSerializer):
    region = RegionSerializer()

    class Meta:
        model = District
        fields = "__all__"


class DistrictKeyValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ("id", "name")


class LGASerializer(serializers.ModelSerializer):
    class Meta:
        model = LGA
        fields = "__all__"


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = "__all__"
