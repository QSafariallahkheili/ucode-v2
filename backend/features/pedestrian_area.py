from functools import lru_cache
import json
from dataclasses import dataclass
from typing import Any, Dict, List
from psycopg_pool import ConnectionPool
from utils import sure_float


@dataclass
class PedestrianArea:
    projectId: str
    surface: str | None
    geom: str | None

def create_pedestrian_area(projectId: str, data_pedestrian) -> List[PedestrianArea]:
    result = []
   
    for f in data_pedestrian["features"]:
        surface = None
        if "surface" in f["properties"]:
            surface = f["properties"]["surface"]

        geom = None
       
        if f["geometry"]["type"] == "Polygon":
            geom = json.dumps(f["geometry"])
        
        if geom is not None:
            tpl = tuple(
                (
                    projectId,
                    surface,
                    geom,
                )
            )
            result.append(tpl)

    return result

def persist_pedestrian_area_polygons(
    conn_pool: ConnectionPool, data_pedestrian: List[PedestrianArea]
):
    with conn_pool.connection() as connection:
        with connection.cursor() as cur:
            insert_query_pedestrian_area = """
                INSERT INTO pedestrian_area (project_id, surface, geom) VALUES (%s, %s, ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326));
            """
            cur.executemany(insert_query_pedestrian_area, data_pedestrian)
            # batching doesn't bare much performance differences here because of the GIS operations involved
            # ps2.execute_batch(cursor, insert_query_building, building_polygons)
            connection.commit()

@lru_cache
def get_pedestrian_area_from_db(conn_pool: ConnectionPool, projectId:str):
    with conn_pool.connection() as connection:
        get_pedestrian_area_query =f''' select json_build_object(
                'type', 'FeatureCollection',
                'features', json_agg(ST_AsGeoJSON(pedestrian_area.*)::json)
                )
                from pedestrian_area
                where project_id = '{projectId}'
            ;
        '''
        pedestrian_area = connection.execute(get_pedestrian_area_query).fetchall()[0][0]
        return pedestrian_area