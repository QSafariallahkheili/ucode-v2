import json

import networkx
import osmnx

from models import BoundingBox


def getDriveNetwork(bbox: BoundingBox) -> str:
    graph = osmnx.graph_from_bbox(
        bbox.ymin, bbox.ymax, bbox.xmin, bbox.xmax, network_type="drive"
    )
    return graph_to_geojson(graph)


def graph_to_geojson(graph: networkx.MultiDiGraph) -> str:
    gdf = osmnx.graph_to_gdfs(graph, nodes=False, edges=True)
    return json.loads(gdf.to_json())
