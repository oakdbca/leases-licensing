import logging

import pytz
import requests
from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.geos.collections import MultiPolygon
from django.core.cache import cache
from ledger_api_client.models import EmailUser
from rest_framework import serializers

logger = logging.getLogger(__name__)


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


def _get_params(
    layer_name, bbox="112.920880404,-35.186088017,129.019915758,-13.5076197999999"
):
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


def get_features_by_multipolygon(multipolygon, layer_name, properties):
    namespace = layer_name.split(":")[0]
    server_path = f"/geoserver/{namespace}/ows"
    params = {
        "service": "WFS",
        "version": "1.0.0",
        "request": "GetFeature",
        "typeName": layer_name,
        "maxFeatures": "5000",
        "srsName": "EPSG:4326",  # using the default projection for open layers and geodjango
        "outputFormat": "application/json",
        "propertyName": properties,
        "CQL_FILTER": f"INTERSECTS(wkb_geometry, {multipolygon.wkt})",
    }
    logger.debug(
        f"Requesting features from {settings.KMI_SERVER_URL}{server_path} with params: {params}"
    )
    if "public" != namespace:
        logger.debug("Using Basic HTTP Auth to access namespace: %s", namespace)
        response = requests.get(
            f"{settings.KMI_SERVER_URL}{server_path}",
            params=params,
            auth=(settings.KMI_AUTH_USERNAME, settings.KMI_AUTH_PASSWORD),
        )
    else:
        response = requests.get(
            f"{settings.KMI_SERVER_URL}{server_path}", params=params
        )

    logger.debug(f"Request took: {response.elapsed.total_seconds()}")
    logger.debug(f"Raw response: {response.text}")
    return response.json()


def get_gis_data_for_proposal(proposal, layer_name, properties):
    """Takes a proposal object and a list of property names and returns a dict of unique values for each property"""
    if not proposal.proposalgeometry.exists():
        logger.debug("ProposalGeometry does not exist for proposal: %s", proposal.id)
        return None

    multipolygon = MultiPolygon(
        list(proposal.proposalgeometry.all().values_list("polygon", flat=True))
    )

    if len(properties) > 1:
        properties_comma_list = ",".join(properties)
    else:
        properties_comma_list = properties[0]
    features = get_features_by_multipolygon(
        multipolygon, layer_name, properties_comma_list
    )
    if 0 == features["totalFeatures"]:
        return None

    logger.info(
        "Found %s features for proposal: %s", features["totalFeatures"], proposal.id
    )
    data = {}
    for prop in properties:
        logger.debug("Getting unique values for property: %s", prop)
        data[prop] = set()

    for feature in features["features"]:
        for prop in properties:
            if prop not in feature["properties"]:
                logger.error("Property %s not found in feature", prop)
                raise AttributeError(f"Property {prop} not found in feature")

            data[prop].add(feature["properties"][prop])

    return data


def polygon_intersects_with_layer(polygon, layer_name):
    """Checks if a polygon intersects with a layer"""
    return polygons_intersect_with_layer([polygon], layer_name)


def polygons_intersect_with_layer(polygons, layer_name):
    """Checks if a polygon intersects with a layer"""
    multipolygon = MultiPolygon(polygons)
    features = get_features_by_multipolygon(
        multipolygon, layer_name=layer_name, properties="objectid"
    )
    if 0 == features["totalFeatures"]:
        return False

    return True


def multipolygon_intersects_with_layer(multipolygon, layer_name):
    """Checks if a multipolygon intersects with a layer"""
    features = get_features_by_multipolygon(
        multipolygon, layer_name=layer_name, properties="objectid"
    )
    if 0 == features["totalFeatures"]:
        return False

    return True


def get_secure_file_url(instance, file_field_name):
    base_path = settings.SECURE_FILE_API_BASE_PATH
    return (
        f"{base_path}{instance._meta.model.__name__}/{instance.id}/{file_field_name}/"
    )


def get_secure_document_url(instance, related_name="documents", document_id=None):
    base_path = settings.SECURE_DOCUMENT_API_BASE_PATH
    if document_id:
        return f"{base_path}{instance._meta.model.__name__}/{instance.id}/{related_name}/{document_id}/"
    return f"{base_path}{instance._meta.model.__name__}/{instance.id}/{related_name}/"
