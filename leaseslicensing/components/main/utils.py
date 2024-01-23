import json
import logging
import os
import re
import sys
from zipfile import ZipFile

import geopandas as gpd
import pytz
import requests
from django.apps import apps
from django.conf import settings
from django.contrib.gis.gdal import SpatialReference
from django.contrib.gis.geos import GEOSGeometry, Polygon
from django.contrib.gis.geos.collections import MultiPolygon
from django.core.cache import cache
from django.db.models import Q
from django.utils import timezone
from ledger_api_client.managed_models import SystemGroup
from ledger_api_client.models import EmailUser
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from leaseslicensing.components.competitive_processes.models import (
    CompetitiveProcessParty,
)
from leaseslicensing.components.tenure.models import (
    LGA,
    Act,
    Category,
    District,
    Identifier,
    Name,
    Region,
    SiteName,
    Tenure,
    Vesting,
)

logger = logging.getLogger(__name__)


def handle_validation_error(e):
    if hasattr(e, "error_dict"):
        raise serializers.ValidationError(repr(e.error_dict))
    else:
        if hasattr(e, "message"):
            raise serializers.ValidationError(e.message)
        else:
            raise


def is_department_user(email):
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


def get_polygon_source(geometry_obj):
    from leaseslicensing.components.competitive_processes.models import (
        CompetitiveProcessGeometry,
    )
    from leaseslicensing.components.proposals.models import ProposalGeometry

    source = ""

    if not geometry_obj.drawn_by:
        source = "Unknown"
    elif isinstance(geometry_obj, ProposalGeometry) and geometry_obj.drawn_by in [
        geometry_obj.proposal.ind_applicant,
    ]:
        # Polygon drawn by individual applicant
        source = "Applicant"
    elif (
        isinstance(geometry_obj, ProposalGeometry)
        and geometry_obj.proposal.org_applicant
        and geometry_obj.drawn_by
        in geometry_obj.proposal.org_applicant.contacts.all().values_list(
            "user", flat=True
        )
    ):
        # Polygon drawn by organisation applicant
        source = "Applicant"
    elif isinstance(
        geometry_obj, CompetitiveProcessGeometry
    ) and geometry_obj.drawn_by in (
        CompetitiveProcessParty.objects.filter(
            competitive_process_id=geometry_obj.competitive_process.id
        )
        .exclude(person_id__isnull=True)
        .values_list("person_id", flat=True)
    ):
        source = "Applicant"
    else:
        assessor_group = SystemGroup.objects.get(name=settings.GROUP_NAME_ASSESSOR)
        if geometry_obj.drawn_by in assessor_group.get_system_group_member_ids():
            source = "Assessor"
        competitive_process_editor_group = SystemGroup.objects.get(
            name=settings.GROUP_COMPETITIVE_PROCESS_EDITOR
        )
        if (
            geometry_obj.drawn_by
            in competitive_process_editor_group.get_system_group_member_ids()
        ):
            source = "Competitive Process Editor"

    return source


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
    logger.info(
        f"Requesting features from {settings.GIS_SERVER_URL}{server_path} with params: {params}"
    )
    if "public" != namespace:
        logger.debug("Using Basic HTTP Auth to access namespace: %s", namespace)
        url = f"{settings.GIS_SERVER_URL}{server_path}"
        response = requests.post(
            url,
            data=params,
            auth=(settings.KMI_AUTH_USERNAME, settings.KMI_AUTH_PASSWORD),
        )
    else:
        response = requests.post(f"{settings.GIS_SERVER_URL}{server_path}", data=params)
    if not response.ok:
        logger.error(f"Error getting features from KMI: {response.text}")
        raise serializers.ValidationError(
            f"Error getting features from KMI (Server URL: {url}, Layer: {layer_name}"
        )

    logger.info(f"Request took: {response.elapsed.total_seconds()}")
    return response.json()


def get_gis_data_for_geometries(instance, geometries_attribute, layer_name, properties):
    """Takes a model instance, the name of the related geometries attribute, the layer name
    and a list of property names and returns a dict of unique values for each property
    """
    if not hasattr(instance, geometries_attribute):
        raise AttributeError(
            f"{instance} does not have attribute {geometries_attribute}"
        )

    geometries = getattr(instance, geometries_attribute)

    if not geometries.exists():
        logger.warn(
            f"No Geometries found for {instance._meta.model.__name__} {instance.lodgement_number}"
        )
        return None

    multipolygon = MultiPolygon(
        list(geometries.all().values_list("polygon", flat=True))
    )
    if not multipolygon.valid:
        from shapely import wkt
        from shapely.validation import explain_validity, make_valid

        logger.warn(
            "Invalid multipolygon for"
            f"{instance._meta.model.__name__} {instance.lodgement_number}: {multipolygon.valid_reason}"
        )

        multipolygon = make_valid(wkt.loads(multipolygon.wkt))
        logger.warn(
            f"Running MakeValid. New validity: {explain_validity(multipolygon)}"
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
        "Found %s features for %s: %s",
        features["totalFeatures"],
        instance._meta.model.__name__,
        instance.lodgement_number,
    )
    data = {}
    for prop in properties:
        logger.info("Getting unique values for property: %s", prop)
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


def save_geometry(request, instance, component, geometry_data, foreign_key_field=None):
    instance_name = instance._meta.model.__name__
    logger.info(f"\n\n\nSaving {instance_name} geometry")

    if not geometry_data:
        logger.warn(f"No {instance_name} geometry to save")
        return

    if not foreign_key_field:
        # this is the name of the foreign key field on the <Instance Type>Geometry model
        # Had to add this as no way to know for sure the name of the foreign key field based on introspection
        # i.e. competitive_process contains an underscore but the django model name does not
        foreign_key_field = instance_name.lower()

    geometry = json.loads(geometry_data)
    InstanceGeometry = apps.get_model("leaseslicensing", f"{instance_name}Geometry")
    if (
        0 == len(geometry["features"])
        and 0
        == InstanceGeometry.objects.filter(**{foreign_key_field: instance}).count()
    ):
        # No feature to save and no feature to delete
        logger.warn(f"{instance_name} geometry has no features to save or delete")
        return

    action = request.data.get("action", None)

    geometry_ids = []
    for feature in geometry.get("features"):
        # check if feature is a polygon, continue if not
        if feature.get("geometry").get("type") != "Polygon":
            logger.warn(
                f"{instance_name}: {instance} contains a feature that is not a polygon: {feature}"
            )
            continue

        # Create a Polygon object from the open layers feature
        polygon = Polygon(feature.get("geometry").get("coordinates")[0])

        # check if it intersects with any of the lands geos
        if not polygon_intersects_with_layer(
            polygon, "public:dbca_legislated_lands_and_waters"
        ):
            # if it doesn't, raise a validation error (this should be prevented in the front end
            # and is here just in case
            raise ValidationError(
                "One or more polygons do not intersect with the DBCA Lands and Waters layer"
            )

        # If it does intersect, save it and set intersects to true
        geometry_data = {
            f"{foreign_key_field}_id": instance.id,
            "polygon": polygon,
            "intersects": True,  # probably redunant now that we are not allowing non-intersecting geometries
        }
        InstanceGeometrySaveSerializer = getattr(
            sys.modules[f"leaseslicensing.components.{component}.serializers"],
            f"{instance_name}GeometrySaveSerializer",
        )
        if feature.get("id"):
            logger.info(
                f"Updating existing {instance_name} geometry: {feature.get('id')} for Proposal: {instance}"
            )
            try:
                geometry = InstanceGeometry.objects.get(id=feature.get("id"))
            except InstanceGeometry.DoesNotExist:
                logger.warn(
                    f"{instance_name} geometry does not exist: {feature.get('id')}"
                )
                continue
            geometry_data["drawn_by"] = geometry.drawn_by
            geometry_data["locked"] = (
                action in ["submit"]
                and geometry.drawn_by == request.user.id
                or geometry.locked
            )
            serializer = InstanceGeometrySaveSerializer(geometry, data=geometry_data)
        else:
            logger.info(f"Creating new geometry for {instance_name}: {instance}")
            geometry_data["drawn_by"] = request.user.id
            geometry_data["locked"] = action in ["submit"]
            serializer = InstanceGeometrySaveSerializer(data=geometry_data)

        serializer.is_valid(raise_exception=True)
        proposalgeometry_instance = serializer.save()
        logger.info(f"Saved {instance_name} geometry: {proposalgeometry_instance}")
        geometry_ids.append(proposalgeometry_instance.id)

    # Remove any proposal geometries from the db that are no longer in the proposal_geometry that was submitted
    # Prevent deletion of polygons that are locked after status change (e.g. after submit)
    # or have been drawn by another user
    deleted_geometries = (
        InstanceGeometry.objects.filter(**{foreign_key_field: instance})
        .exclude(Q(id__in=geometry_ids) | Q(locked=True) | ~Q(drawn_by=request.user.id))
        .delete()
    )
    if deleted_geometries[0] > 0:
        logger.info(
            f"Deleted {instance_name} geometries: {deleted_geometries} for {instance}"
        )


def populate_gis_data(instance, geometries_attribute, foreign_key_field=None):
    """Fetches required GIS data from KMI and saves it to the instance (Proposal or Competitive Process)
    Todo: Will need to update this to use the new KB GIS modernisation API"""
    instance_name = instance._meta.model.__name__

    logger.info(
        "Populating GIS data for %s: %s", instance_name, instance.lodgement_number
    )

    if not foreign_key_field:
        foreign_key_field = instance_name.lower()

    populate_gis_data_lands_and_waters(
        instance, geometries_attribute, foreign_key_field
    )  # Covers Identifiers, Names, Acts, Tenures and Categories
    populate_gis_data_regions(instance, geometries_attribute, foreign_key_field)
    populate_gis_data_districts(instance, geometries_attribute, foreign_key_field)
    populate_gis_data_lgas(instance, geometries_attribute, foreign_key_field)
    logger.info(
        "-> Finished populating GIS data for %s: %s",
        instance_name,
        instance.lodgement_number,
    )


def populate_gis_data_lands_and_waters(
    instance, geometries_attribute, foreign_key_field
):
    properties = [
        "leg_identifier",
        "leg_vesting",
        "leg_name",
        "leg_tenure",
        "leg_act",
        "category",
    ]
    # Start with storing the ids of existing identifiers, names, acts, tenures and categories of this instance
    # Remove any GIS data thtat is returned from querying the geoserver.
    # Whatever remains in this list is no longer part of this instance and will be deleted.
    object_ids = gis_property_to_model_ids(instance, properties, foreign_key_field)
    gis_data_lands_and_waters = get_gis_data_for_geometries(
        instance,
        geometries_attribute,
        "public:dbca_legislated_lands_and_waters",
        properties,
    )
    if gis_data_lands_and_waters is None:
        logger.warn(
            "No GIS Lands and waters data found for %s %s",
            instance._meta.model.__name__,
            instance.lodgement_number,
        )
        # Delete all the GIS data for this proposal
        delete_gis_data(instance, foreign_key_field, ids_to_delete=object_ids)
        return

    # This part could be refactored to be more generic
    index = 0
    if gis_data_lands_and_waters[properties[index]]:
        for identifier_name in gis_data_lands_and_waters[properties[index]]:
            if not identifier_name.strip():
                continue
            identifier, created = Identifier.objects.get_or_create(name=identifier_name)
            if created:
                logger.info(f"New Identifier created from GIS Data: {identifier}")
            InstanceIdentifier = apps.get_model(
                "leaseslicensing", f"{instance.__class__.__name__}Identifier"
            )
            obj, created = InstanceIdentifier.objects.get_or_create(
                **{foreign_key_field: instance}, identifier=identifier
            )
            if not created:
                # Can only remove from to-delete list if this GIS data was already in the database
                object_ids[properties[index]].remove(obj.id)

    index += 1
    if gis_data_lands_and_waters[properties[index]]:
        for vesting_name in gis_data_lands_and_waters[properties[index]]:
            if not vesting_name.strip():
                continue
            vesting, created = Vesting.objects.get_or_create(name=vesting_name)
            if created:
                logger.info(f"New Vesting created from GIS Data: {vesting}")
            InstanceVesting = apps.get_model(
                "leaseslicensing", f"{instance.__class__.__name__}Vesting"
            )
            obj, created = InstanceVesting.objects.get_or_create(
                **{foreign_key_field: instance}, vesting=vesting
            )
            if not created:
                object_ids[properties[index]].remove(obj.id)

    index += 1
    if gis_data_lands_and_waters[properties[index]]:
        for name_name in gis_data_lands_and_waters[properties[index]]:
            # Yes, name_name is a pretty silly variable name, what would you call it?
            if not name_name.strip():
                continue
            name, created = Name.objects.get_or_create(name=name_name)
            if created:
                logger.info(f"New Name created from GIS Data: {name}")
            InstanceName = apps.get_model(
                "leaseslicensing", f"{instance.__class__.__name__}Name"
            )
            obj, created = InstanceName.objects.get_or_create(
                **{foreign_key_field: instance}, name=name
            )
            if not created:
                object_ids[properties[index]].remove(obj.id)

    index += 1
    if gis_data_lands_and_waters[properties[index]]:
        for tenure_name in gis_data_lands_and_waters[properties[index]]:
            if not tenure_name.strip():
                continue
            tenure, created = Tenure.objects.get_or_create(name=tenure_name)
            if created:
                logger.info(f"New Tenure created from GIS Data: {tenure}")
            InstanceTenure = apps.get_model(
                "leaseslicensing", f"{instance.__class__.__name__}Tenure"
            )
            obj, created = InstanceTenure.objects.get_or_create(
                **{foreign_key_field: instance}, tenure=tenure
            )
            if not created:
                object_ids[properties[index]].remove(obj.id)

    index += 1
    if gis_data_lands_and_waters[properties[index]]:
        for act_name in gis_data_lands_and_waters[properties[index]]:
            if not act_name.strip():
                continue
            act, created = Act.objects.get_or_create(name=act_name)
            if created:
                logger.info(f"New Act created from GIS Data: {act}")
            InstanceAct = apps.get_model(
                "leaseslicensing", f"{instance.__class__.__name__}Act"
            )
            obj, created = InstanceAct.objects.get_or_create(
                **{foreign_key_field: instance}, act=act
            )
            if not created:
                object_ids[properties[index]].remove(obj.id)

    index += 1
    if gis_data_lands_and_waters[properties[index]]:
        for category_name in gis_data_lands_and_waters[properties[index]]:
            if not category_name.strip():
                continue
            category, created = Category.objects.get_or_create(name=category_name)
            if created:
                logger.info(f"New Category created from GIS Data: {category}")
            InstanceCategory = apps.get_model(
                "leaseslicensing", f"{instance.__class__.__name__}Category"
            )
            obj, created = InstanceCategory.objects.get_or_create(
                **{foreign_key_field: instance}, category=category
            )
            if not created:
                object_ids[properties[index]].remove(obj.id)

    delete_gis_data(instance, foreign_key_field, ids_to_delete=object_ids)


def populate_gis_data_regions(instance, geometries_attribute, foreign_key_field):
    properties = [
        "drg_region_name",
    ]
    object_ids = gis_property_to_model_ids(instance, properties, foreign_key_field)
    gis_data_regions = get_gis_data_for_geometries(
        instance, geometries_attribute, "cddp:dbca_regions", properties
    )
    if gis_data_regions is None:
        logger.warn(
            "No GIS Region data found for instance %s", instance.lodgement_number
        )
        delete_gis_data(instance, foreign_key_field, ids_to_delete=object_ids)
        return

    if gis_data_regions[properties[0]]:
        for region_name in gis_data_regions[properties[0]]:
            region, created = Region.objects.get_or_create(name=region_name)
            if created:
                logger.info(f"New Region created from GIS Data: {region}")
            InstanceDistrict = apps.get_model(
                "leaseslicensing", f"{instance.__class__.__name__}Region"
            )
            obj, created = InstanceDistrict.objects.get_or_create(
                **{foreign_key_field: instance}, region=region
            )
            if not created:
                object_ids[properties[0]].remove(obj.id)

    delete_gis_data(instance, foreign_key_field, ids_to_delete=object_ids)


def populate_gis_data_districts(instance, geometries_attribute, foreign_key_field):
    properties = [
        "district",
    ]
    object_ids = gis_property_to_model_ids(instance, properties, foreign_key_field)
    gis_data_districts = get_gis_data_for_geometries(
        instance, geometries_attribute, "cddp:dbca_districts", properties
    )
    if gis_data_districts is None:
        logger.warn(
            "No GIS District data found for instance %s", instance.lodgement_number
        )
        delete_gis_data(instance, foreign_key_field, ids_to_delete=object_ids)
        return

    if gis_data_districts[properties[0]]:
        for district_name in gis_data_districts[properties[0]]:
            district, created = District.objects.get_or_create(name=district_name)
            if created:
                logger.info(f"New Region created from GIS Data: {district}")
            InstanceDistrict = apps.get_model(
                "leaseslicensing", f"{instance.__class__.__name__}District"
            )
            obj, created = InstanceDistrict.objects.get_or_create(
                **{foreign_key_field: instance}, district=district
            )
            if not created:
                object_ids[properties[0]].remove(obj.id)

    delete_gis_data(instance, foreign_key_field, ids_to_delete=object_ids)


def populate_gis_data_lgas(instance, geometries_attribute, foreign_key_field):
    properties = [
        "lga_label",
    ]
    object_ids = gis_property_to_model_ids(instance, properties, foreign_key_field)
    gis_data_lgas = get_gis_data_for_geometries(
        instance, geometries_attribute, "cddp:local_gov_authority", properties
    )
    if gis_data_lgas is None:
        logger.warn("No GIS LGA data found for instance %s", instance.lodgement_number)
        delete_gis_data(instance, foreign_key_field, ids_to_delete=object_ids)
        return

    if gis_data_lgas[properties[0]]:
        for lga_name in gis_data_lgas[properties[0]]:
            lga, created = LGA.objects.get_or_create(name=lga_name)
            if created:
                logger.info(f"New LGA created from GIS Data: {lga}")
            InstanceLGA = apps.get_model(
                "leaseslicensing", f"{instance.__class__.__name__}LGA"
            )
            obj, created = InstanceLGA.objects.get_or_create(
                **{foreign_key_field: instance}, lga=lga
            )
            if not created:
                object_ids[properties[0]].remove(obj.id)

    delete_gis_data(instance, foreign_key_field, ids_to_delete=object_ids)


def delete_gis_data(instance, foreign_key_field, ids_to_delete=[]):
    """
    Deletes all GIS data objects for the given instance that are in the ids_to_delete list.
    The function tries to map GIS data property names to InstanceXyz model names. E.g.
    'leg_identifier' to InstanceIdentifier, 'category' to InstanceCategory

    Args:
        instance (Proposal or CompetitiveProcess model at this stage):
            An instance of a proposal or competitive process model object
        ids_to_delete (dict):
            A dictionary that maps GIS data property names to lists of object ids to delete
            Example: {'leg_identifier': [1,2,3], 'leg_vesting': [4,5], 'category': []}
    """

    for key in ids_to_delete:
        # Instance GIS data is stored in InstanceXyz models.
        # This matches for the Xyz part of the model name from GIS data property name
        class_class = _gis_property_to_model(
            instance, key
        )  # ----< missing arguement !J?!
        if class_class is None:
            continue
        # Delete all objects of the class belonging to this instance that are in the ids_to_delete list
        deleted = class_class.objects.filter(
            Q(**{foreign_key_field: instance}) & Q(id__in=ids_to_delete[key])
        ).delete()
        if deleted[0] > 0:
            logger.info(
                f"Deleted {class_class.__name__} {deleted} from "
                f"{instance._meta.model.__name__} {instance.lodgement_number}"
            )


def gis_property_to_model_ids(instance, properties, foreign_key_field):
    """
    Maps GIS data property names to <Instance>Xyz model class names and returns a dictionary of
    property names and lists of object ids for the respective <Instance>Xyz model that
    belongs to the property.

    Returns:
        A dictionary that maps GIS data property names to lists of object ids
        Example: {'leg_identifier': [1,2,3], 'leg_vesting': [4,5], 'category': []}

    Args:
        instance (object):
            A Proposal or CompetitiveProcess object
        properties (list)):
            A list of GIS data property names
    """

    property_model_map = {p: _gis_property_to_model(instance, p) for p in properties}

    return {
        p: []
        if property_model_map[p] is None
        else list(
            property_model_map[p]
            .objects.filter(**{foreign_key_field: instance})
            .distinct()
            .values_list("id", flat=True)
        )
        for p in property_model_map
    }


def _gis_property_to_model(instance, property):
    """
    Returns the respective model class for a GIS data property name.

    Args:
        instance (object):
            A Proposal or CompetitiveProcess model instance
        property (str):
            A GIS data property name
    """

    # Catches all GIS data property names currently returned by the geoserver
    # Groups 1 and 3 are non-capturing prefixes and suffixes, with group 2 being
    # the actual Xyz part of the class name.
    regex = r"^(?:leg_|drg_)?([a-zA-Z_]+?)(?:_name|_label)?$"
    match = re.match(regex, property)
    if match is None:
        logger.warning(f"Could not match property {property}")
        return None

    # Compile the class name from the matched group
    class_name = f"{instance.__class__.__name__.lower()}{match.group(1)}"
    # Get the class object from the app registry
    try:
        class_class = apps.get_model(app_label="leaseslicensing", model_name=class_name)
    except LookupError:
        logger.exception(f"Could not find class {class_name}")
        return None

    return class_class


def save_site_name(instance, site_name):
    if not site_name and not instance.site_name:
        return

    if not site_name:
        instance.site_name = None
        instance.save()

    site_name, created = SiteName.objects.get_or_create(name=site_name)
    if created:
        logger.info(f"New Site Name created: {site_name}")
    instance.site_name = site_name
    instance.save()


def save_groups_data(instance, groups_data, foreign_key_field=None):
    instance_name = instance.__class__.__name__
    if not foreign_key_field:
        foreign_key_field = instance_name.lower()

    InstanceGroup = apps.get_model("leaseslicensing", f"{instance_name}Group")

    if not groups_data:
        delete_results = (
            InstanceGroup.objects.filter(**{foreign_key_field: instance})
            .exclude()
            .delete()
        )
        if delete_results[0] > 0:
            logger.info(f"Deleted {delete_results} groups for {instance}")

    if not groups_data or 0 == len(groups_data):
        return
    group_ids = []
    for group in groups_data:
        instance_group, created = InstanceGroup.objects.get_or_create(
            **{foreign_key_field: instance}, group_id=group["id"]
        )
        if created:
            logger.info(f"Added Application: {instance} to Group: {instance_group}")
        group_ids.append(group["id"])
    delete_results = (
        InstanceGroup.objects.filter(**{foreign_key_field: instance})
        .exclude(group_id__in=group_ids)
        .delete()
    )
    if delete_results[0] > 0:
        logger.info(f"Deleted {delete_results} groups for {instance}")


def get_secure_file_url(instance, file_field_name, revision_id=None):
    base_path = settings.SECURE_FILE_API_BASE_PATH
    if revision_id:
        return f"{base_path}{instance._meta.model.__name__}/{instance.id}/{file_field_name}/{revision_id}/"
    return (
        f"{base_path}{instance._meta.model.__name__}/{instance.id}/{file_field_name}/"
    )


def get_secure_document_url(instance, related_name="documents", document_id=None):
    base_path = settings.SECURE_DOCUMENT_API_BASE_PATH
    if document_id:
        return f"{base_path}{instance._meta.model.__name__}/{instance.id}/{related_name}/{document_id}/"
    return f"{base_path}{instance._meta.model.__name__}/{instance.id}/{related_name}/"


def validate_map_files(request, instance, foreign_key_field=None):
    # Validates shapefiles uploaded with via the proposal map or the competitive process map.
    # Shapefiles are valid when the shp, shx, and dbf extensions are provided
    # and when they intersect with DBCA legislated land or water polygons

    valid_geometry_saved = False

    logger.debug(f"Shapefile documents: {instance.shapefile_documents.all()}")

    if not instance.shapefile_documents.exists():
        raise ValidationError(
            "Please attach at least a .shp, .shx, and .dbf file (the .prj file is optional but recommended)"
        )

    # Shapefile extensions shp (geometry), shx (index between shp and dbf), dbf (data) are essential
    shp_file_qs = instance.shapefile_documents.filter(
        Q(name__endswith=".shp")
        | Q(name__endswith=".shx")
        | Q(name__endswith=".dbf")
        | Q(name__endswith=".prj")
    )

    # Validate shapefile and all the other related files are present
    if not shp_file_qs:
        raise ValidationError(
            "You can only attach files with the following extensions: .shp, .shx, and .dbf"
        )

    shp_files = shp_file_qs.filter(name__endswith=".shp").count()
    shx_files = shp_file_qs.filter(name__endswith=".shx").count()
    dbf_files = shp_file_qs.filter(name__endswith=".dbf").count()

    if shp_files != 1 or shx_files != 1 or dbf_files != 1:
        raise ValidationError(
            "Please attach at least a .shp, .shx, and .dbf file (the .prj file is optional but recommended)"
        )

    # Add the shapefiles to a zip file for archiving purposes
    # (as they are deleted after being converted to proposal geometry)
    shapefile_archive_name = (
        os.path.splitext(instance.shapefile_documents.first().path)[0]
        + "-"
        + timezone.now().strftime("%Y%m%d%H%M%S")
        + ".zip"
    )
    shapefile_archive = ZipFile(shapefile_archive_name, "w")
    for shp_file_obj in shp_file_qs:
        shapefile_archive.write(shp_file_obj.path, shp_file_obj.name)
    shapefile_archive.close()

    # A list of all uploaded shapefiles
    shp_file_objs = shp_file_qs.filter(Q(name__endswith=".shp"))

    for shp_file_obj in shp_file_objs:
        gdf = gpd.read_file(shp_file_obj.path)  # Shapefile to GeoDataFrame

        # If no prj file assume WGS-84 datum
        if not gdf.crs:
            gdf_transform = gdf.set_crs("epsg:4326", inplace=True)
        else:
            gdf_transform = gdf.to_crs("epsg:4326")

        geometries = gdf.geometry  # GeoSeries

        # Only accept polygons
        geom_type = geometries.geom_type.values[0]
        if geom_type not in ("Polygon", "MultiPolygon"):
            raise ValidationError(f"Geometry of type {geom_type} not allowed")

        # Check for intersection with DBCA geometries
        gdf_transform["valid"] = False
        for geom in geometries:
            srid = SpatialReference(
                geometries.crs.srs
            ).srid  # spatial reference identifier

            polygon = GEOSGeometry(geom.wkt, srid=srid)

            # Add the file name as identifier to the geojson for use in the frontend
            if "source_" not in gdf_transform:
                gdf_transform["source_"] = shp_file_obj.name

            # Imported geometry is valid if it intersects with any one of the DBCA geometries
            if not polygon_intersects_with_layer(
                polygon, "public:dbca_legislated_lands_and_waters"
            ):
                raise ValidationError(
                    "One or more polygons does not intersect with a relevant layer"
                )

            gdf_transform["valid"] = True

            # Some generic code to save the geometry to the database
            # That will work for both a proposal instance and a competitive process instance
            instance_name = instance._meta.model.__name__

            if not foreign_key_field:
                foreign_key_field = instance_name.lower()

            geometry_model = apps.get_model(
                "leaseslicensing", f"{instance_name}Geometry"
            )

            geometry_model.objects.create(
                **{
                    foreign_key_field: instance,
                    "polygon": polygon,
                    "intersects": True,
                    "drawn_by": request.user.id,
                }
            )

        instance.save()
        valid_geometry_saved = True

    # Delete all shapefile documents so the user can upload another one if they wish.
    instance.shapefile_documents.all().delete()

    return valid_geometry_saved
