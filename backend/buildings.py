import json
from dataclasses import dataclass
from typing import Any, List

import psycopg2.extras as ps2

from utils import sure_float


@dataclass
class BuildingPolygons:
    projectId: str
    wallcolor: str | None
    wallmaterial: str | None
    roofcolor: str | None
    roofmaterial: str | None
    roofshape: str | None
    roofheight: float | None
    height: float | None
    floors: float | None
    estimatedheight: float | None
    amenity: Any
    geom: str | None


def create_building_polygons(projectId: str, data_building) -> List[BuildingPolygons]:
    result = []
    for f in data_building["elements"]:
        # print(f)
        f["geometry"]["type"] = "Polygon"
        f["geometry"]["coordinates"] = [f["geometry"]["coordinates"]]
    for f in data_building["elements"]:
        # print(f)
        wallcolor = None
        if "building:colour" in f["tags"]:
            wallcolor = f["tags"]["building:colour"]
        wallmaterial = None
        if "building:material" in f["tags"]:
            wallmaterial = f["tags"]["building:material"]
        roofcolor = None
        if "roof:colour" in f["tags"]:
            roofcolor = f["tags"]["roof:colour"]
        roofmaterial = None
        if "roof:material" in f["tags"]:
            roofmaterial = f["tags"]["roof:material"]
        roofshape = None
        if "roof:shape" in f["tags"]:
            roofshape = f["tags"]["roof:shape"]
        roofheight = None
        if "roof:height" in f["tags"]:
            roofheight = f["tags"]["roof:height"]
            if "," in roofheight:
                roofheight = roofheight.replace(",", ".")
        height = None
        if "height" in f["tags"]:
            height = f["tags"]["height"]
            height = sure_float(height)
        floors = None
        if "building:levels" in f["tags"]:
            floors = f["tags"]["building:levels"]
            floors = sure_float(floors)

        estimatedheight = None
        if height is not None:
            estimatedheight = sure_float(height)
        elif floors is not None:
            estimatedheight = sure_float(floors) * 3.5
        else:
            estimatedheight = 15

        amenity = None
        if "amenity" in f["tags"]:
            amenity = f["tags"]["amenity"]
        geom = json.dumps(f["geometry"])
        # print(geom)
        tpl = tuple(
            (
                projectId,
                wallcolor,
                wallmaterial,
                roofcolor,
                roofmaterial,
                roofshape,
                roofheight,
                height,
                floors,
                estimatedheight,
                amenity,
                geom,
            )
        )
        result.append(tpl)

    return result

def persist_building_polygons(connection:Any, building_polygons:List[BuildingPolygons]):
   
    cursor = connection.cursor()
    insert_query_building = """
        INSERT INTO building (project_id,wallcolor,wallmaterial, roofcolor,roofmaterial,roofshape,roofheight, height, floors, estimatedheight, amenity, geom) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s, ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326));
    """
    cursor.executemany(insert_query_building, building_polygons)
    # batching doesn't bare much performance differences here because of the GIS operations involved
    #ps2.execute_batch(cursor, insert_query_building, building_polygons)
    connection.commit()
    cursor.close()
    connection.close()
  