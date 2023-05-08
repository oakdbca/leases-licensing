from rest_framework import serializers

from leaseslicensing.components.tenure.models import (
    LGA,
    Act,
    Category,
    District,
    Group,
    Region,
    SiteName,
    Tenure,
)


class ActSerializer(serializers.ModelSerializer):
    class Meta:
        model = Act
        fields = "__all__"


class TenureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenure
        fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


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


class SiteNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteName
        fields = "__all__"
