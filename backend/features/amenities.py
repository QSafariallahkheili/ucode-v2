from functools import lru_cache
import json
from dataclasses import dataclass
from typing import Any, Dict, List
from psycopg_pool import ConnectionPool
from utils import sure_float


@dataclass
class AmenitiesPolygons:
    projectId: str
    buildingId: float | None
    amenity: Any
    geom: str | None

def create_amenities_polygons(projectId: str, data_amenities) -> List[AmenitiesPolygons]:
    result = []
    for f in data_amenities['features']:
        if f['geometry']['type'] != 'Polygon':
            continue
        buildingId= None
        if "id" in f:
            buildingId = f["id"]
        amenity = None
        if "amenity" in f['properties']:
            amenity = f['properties']["amenity"]
        estimatedHeight = None
        amenityName = None
        if "name" in f['properties']:
            amenityName = f['properties']["name"]
        else:
            amenityName =f['properties']['amenity']
        geom = json.dumps(f["geometry"])
       
        tpl = tuple(
            (
                projectId,
                buildingId,
                estimatedHeight,
                amenity,
                amenityName,
                geom,
            )
        )
        result.append(tpl)
    return result

def persist_amenities_polygons(
    conn_pool: ConnectionPool, amenity_polygons: List[AmenitiesPolygons]
):
    with conn_pool.connection() as connection:
        with connection.cursor() as cur:
            insert_query_amenities = """
                INSERT INTO amenities (project_id,building_id,estimatedheight,amenity, amenity_name,geom) VALUES (%s,%s, %s, %s, %s, ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326));
            """
            cur.executemany(insert_query_amenities, amenity_polygons)
            connection.commit()

@lru_cache
def get_amenities_from_db(conn_pool: ConnectionPool, projectId:str):
    with conn_pool.connection() as connection:
        get_amenities_query =f'''
            with candidate_buildings as 
            (select building.geom, building.estimatedheight, amenities.amenity, amenities.amenity_name, amenities.id as amenityid
            from amenities, building 
            where st_isvalid(building.geom) and
                    st_isvalid(amenities.geom) and building.project_id='{projectId}' and amenities.project_id='{projectId}'
                    and st_within(building.geom,amenities.geom) or st_within(amenities.geom, building.geom) and amenities.project_id='{projectId}'
            )

            select json_build_object(
                'type', 'FeatureCollection',
                'features', json_agg(ST_AsGeoJSON(amenities.*)::json)
                )
                from  (
                    select distinct on 
                    (amenityid) amenityid, amenity_name, geom, estimatedheight, amenity FROM candidate_buildings Y 
                    WHERE estimatedheight = 
                    (SELECT max(estimatedheight) FROM candidate_buildings X
                    WHERE X.amenityid = Y.amenityid
                    )
                ) amenities
            ;
        '''
        amenities = connection.execute(get_amenities_query).fetchall()[0][0]
        return amenities
