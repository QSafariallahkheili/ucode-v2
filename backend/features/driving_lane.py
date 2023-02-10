import json
from dataclasses import dataclass
from typing import Any, List
from psycopg_pool import ConnectionPool
from utils import sure_float


@dataclass
class DrivingLanePolygons:
    projectId: str
    lanes: Any
    length: Any
    maxspeed: Any
    width: Any
    highway: Any
    geom: str | None


def create_service_road_polygons(
    projectId: str, data_serviceroad_geojson
) -> List[DrivingLanePolygons]:
    result = []
    for f in data_serviceroad_geojson["features"]:
        if f["geometry"]["type"] == "LineString":
            lanes = None
            if "lanes" in f["properties"]:
                lanes = f["properties"]["lanes"]
            length = None
            if "length" in f["properties"]:
                length = f["properties"]["length"]
            maxspeed = None
            if "maxspeed" in f["properties"]:
                maxspeed = f["properties"]["maxspeed"]
            highway = None
            if "highway" in f["properties"]:
                highway = f["properties"]["highway"]
            width = 2
            geom = json.dumps(f["geometry"])
            tpl = {
                "projectId": projectId,
                "lanes": lanes,
                "length": length,
                "maxspeed": maxspeed,
                "width": width,
                "highway": highway,
                "geom": geom,
            }
            result.append(tpl)
    return result


def create_driving_lane_polygons(projectId: str, road) -> List[DrivingLanePolygons]:
    result = []
    for f in road["features"]:
        # print(f)
        geom = json.dumps(f["geometry"])
        lanes = None
        if "lanes" in f["properties"]:
            lanes = f["properties"]["lanes"]
        length = None
        if "length" in f["properties"]:
            length = f["properties"]["length"]
        maxspeed = None
        if "maxspeed" in f["properties"]:
            maxspeed = f["properties"]["maxspeed"]

        highway = None
        if "highway" in f["properties"]:
            highway = f["properties"]["highway"]

        width = None
        if (
            "width" in f["properties"]
            and f["properties"]["width"] is not None
            and isinstance(f["properties"]["width"], str)
        ):
            width = f["properties"]["width"]
            width = sure_float(width)
        elif f["properties"]["highway"] == "primary":
            width = 10
        elif (
            f["properties"]["highway"] == "secondary"
            or f["properties"]["highway"] == "secondary_link"
        ):
            width = 8
        elif (
            f["properties"]["highway"] == "tertiary"
            or f["properties"]["highway"] == "tertiary_link"
        ):
            width = 6
        elif (
            f["properties"]["highway"] == "residential"
            or f["properties"]["highway"] == "living_street"
        ):
            width = 4
        else:
            width = 4
        tpl = {
            "projectId": projectId,
            "lanes": lanes,
            "length": length,
            "maxspeed": maxspeed,
            "width": width,
            "highway": highway,
            "geom": geom,
        }
        result.append(tpl)
    return result


def persist_driving_lane(
    conn_pool: ConnectionPool, driving_lane_polygons: List[DrivingLanePolygons]
):
    with conn_pool.connection() as connection:
        with connection.cursor() as cur:
            insert_query_driving_lane = """
              INSERT INTO driving_lane (project_id,lanes,length,maxspeed,width, highway, geom) VALUES (%(projectId)s,%(lanes)s,%(length)s,%(maxspeed)s,%(width)s,%(highway)s, ST_SetSRID(st_astext(st_geomfromgeojson(%(geom)s)), 4326));
            """
            cur.executemany(insert_query_driving_lane, driving_lane_polygons)
            connection.commit()


def persist_driving_lane_polygon(
    conn_pool: ConnectionPool, driving_lane_polygons: List[DrivingLanePolygons]
):
    with conn_pool.connection() as connection:
        with connection.cursor() as cur:
            insert_query_driving_lane = """
            INSERT INTO driving_lane_polygon (project_id,lanes,length,maxspeed,width,highway, geom) VALUES (%(projectId)s,%(lanes)s,%(length)s,%(maxspeed)s,%(width)s,%(highway)s,
            st_buffer(
                ST_SetSRID(ST_GeomFromGeoJSON(%(geom)s), 4326)::geography,
                (%(width)s::double precision)/2 ,
                'endcap=round join=round quad_segs=2')::geometry
            );
            """
            cur.executemany(insert_query_driving_lane, driving_lane_polygons)
            connection.commit()
