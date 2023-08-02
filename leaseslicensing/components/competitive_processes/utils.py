from leaseslicensing.components.competitive_processes.models import CompetitiveProcessGeometry
from leaseslicensing.components.competitive_processes.serializers import CompetitiveProcessGeometrySaveSerializer, CompetitiveProcessMapFeatureInfoSerializer

def get_competitive_process_geometries_for_map_component(
    competitive_process, context, feature_collection
):

    if not feature_collection:
        feature_collection = {"type": "FeatureCollection", "features": []}

    cp_geoms = CompetitiveProcessGeometry.objects.none()
    if competitive_process:
        cp_geoms = CompetitiveProcessGeometry.objects.filter(
            competitive_process_id=competitive_process.id
        )

    for geom in cp_geoms:
        g = CompetitiveProcessGeometrySaveSerializer(geom, context=context).data
        g["properties"]["source"] = "competitive_process"
        g["model"] = CompetitiveProcessMapFeatureInfoSerializer(
            geom.competitive_process, context=context
        ).data
        feature_collection["features"].append(g)

    return feature_collection
