import pytz
import requests
from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry
from django.core.cache import cache
from ledger_api_client.models import EmailUser
from rest_framework import serializers


def handle_validation_error(e):
    if hasattr(e, "error_dict"):
        raise serializers.ValidationError(repr(e.error_dict))
    else:
        if hasattr(e, "message"):
            raise serializers.ValidationError(e.message)
        else:
            raise


def get_department_user(email):
    if (
        EmailUser.objects.filter(email__iexact=email.strip())
        and EmailUser.objects.get(email__iexact=email.strip()).is_staff
    ):
        return True
    return False


def to_local_tz(_date):
    local_tz = pytz.timezone(settings.TIME_ZONE)
    return _date.astimezone(local_tz)


def _get_params(layer_name):
    return {
        "SERVICE": "WFS",
        "VERSION": "1.0.0",
        "REQUEST": "GetFeature",
        "typeName": layer_name,
        "maxFeatures": 50000,
        "outputFormat": "application/json",
    }


def get_dbca_lands_and_waters_geojson():
    data = cache.get(settings.CACHE_KEY_DBCA_LEGISLATED_LANDS_AND_WATERS)
    if not data:
        URL = "https://kmi.dpaw.wa.gov.au/geoserver/public/ows"
        PARAMS = _get_params("public:dbca_legislated_lands_and_waters")
        res = requests.get(url=URL, params=PARAMS)
        data = res.json()
        cache.set(
            settings.CACHE_KEY_DBCA_LEGISLATED_LANDS_AND_WATERS,
            data,
            settings.LOV_CACHE_TIMEOUT,
        )
    return data


def get_dbca_lands_and_waters_geos():
    geojson = get_dbca_lands_and_waters_geojson()
    geoms = []
    for feature in geojson.get("features"):
        feature_geom = feature.get("geometry")
        geos_geom = GEOSGeometry(f"{feature_geom}").prepared
        geoms.append(geos_geom)
    return geoms
