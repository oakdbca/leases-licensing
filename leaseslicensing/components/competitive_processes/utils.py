import json
from django.db.models import Q
from django.contrib.gis.gdal import SpatialReference
from django.contrib.gis.geos import GEOSGeometry, Polygon, LinearRing

from rest_framework import serializers

from leaseslicensing.components.proposals.models import ProposalGeometry
from leaseslicensing.components.competitive_processes.models import CompetitiveProcessGeometry
from leaseslicensing.components.competitive_processes.serializers import CompetitiveProcessGeometrySerializer
from leaseslicensing.components.main.utils import get_dbca_lands_and_waters_geos


def format_data(competitive_process):
    for party in competitive_process.get('competitive_process_parties', []):
        for party_detail in party.get('party_details', []):
            if 'temporary_data' in party_detail:
                party_detail['detail'] = party_detail['temporary_data']['detail']
                party_detail['created_by_id'] = party_detail['temporary_data']['accessing_user']['id']
    return competitive_process


def save_geometry(request, instance, geometry, action_name):
    # geometry
    geometry = json.loads(geometry) if isinstance(geometry, str) else geometry
    lands_geos_data = get_dbca_lands_and_waters_geos()
    e4283 = SpatialReference("EPSG:4283")  # EPSG string
    # Concat proposal geometries (if exist) and competitive process geometries
    proposal_geometries = list(instance.originating_proposal.proposalgeometry.all()
                               .exclude(Q(locked=True) | ~Q(drawn_by=request.user.id))
                               ) \
                                if hasattr(instance, "originating_proposal") \
                                    else []
    polygons_to_delete = list(instance.competitive_process_geometries.all()
                              .exclude(Q(locked=True) | ~Q(drawn_by=request.user.id))
                              ) + \
                                proposal_geometries

    # Ability for assesssor to replace or adjust the polygons
    for feature in geometry.get("features"):
        polygon = None
        intersects = False

        if feature.get("geometry").get("type") == "Polygon":
            feature_dict = feature.get("geometry")
            geos_repr = GEOSGeometry("{}".format(feature_dict))
            geos_repr_transform = geos_repr.transform(e4283, clone=True)
            for geom in lands_geos_data:
                if geom.intersects(geos_repr_transform):
                    intersects = True
                    break
            linear_ring = LinearRing(feature_dict.get("coordinates")[0])
            polygon = Polygon(linear_ring)

        data = {
           "competitive_process_id": instance.id,
           "polygon": polygon,
           "intersects": intersects,
        }

        if geometry and feature.get("id"):
            # Update existing polygon
            source = feature.get("properties", {"source": None}).get("source", None)
            if source in ["competitive_process"]:
                geom = CompetitiveProcessGeometry.objects.get(id=feature.get("id"))
            elif source in ["registration_of_interest"]:
                geom = ProposalGeometry.objects.get(id=feature.get("id"))
            else:
                raise serializers.ValidationError(
                    f"Error fetching geometry for source {source}")

            data["drawn_by"] = geom.drawn_by if geom.drawn_by else request.user.id
            data["locked"] = action_name in ["complete"] and geom.drawn_by == request.user.id or geom.locked

            if geom in polygons_to_delete:
                polygons_to_delete.remove(geom)
            serializer = CompetitiveProcessGeometrySerializer(
                geom,
                data=data,
                context={"action": action_name,},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
        elif geometry:
            data["drawn_by"] = request.user.id
            data["locked"] = action_name in ["complete"]
            # Create new polygon
            serializer = CompetitiveProcessGeometrySerializer(
                data=data,
                context={"action": action_name,},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

    # delete polygons not returned from the front end
    [poly.delete() for poly in polygons_to_delete]

