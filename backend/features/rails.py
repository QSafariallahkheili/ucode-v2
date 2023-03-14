from functools import lru_cache
import json
from dataclasses import dataclass
from typing import Any, Dict, List
from psycopg_pool import ConnectionPool
from utils import sure_float

@dataclass
class Rails:
    projectId: str
    geom: str | None

def create_rails(projectId: str, data_rails) -> List[Rails]:

    result = []
    for f in data_rails["features"]:
        if f["geometry"]["type"] == "LineString":
            geom = json.dumps(f["geometry"])
            tpl = {
                "projectId": projectId,
                "geom": geom,
            }
            result.append(tpl)
    return result

def persist_rails(
    conn_pool: ConnectionPool, data_rails: List[Rails]
):
    with conn_pool.connection() as connection:
        with connection.cursor() as cur:
            insert_query_rails = """
              INSERT INTO rails (project_id, geom) VALUES (%(projectId)s, ST_SetSRID(st_astext(st_geomfromgeojson(%(geom)s)), 4326));
            """
            cur.executemany(insert_query_rails, data_rails)
            connection.commit()

def refine_rails(conn_pool: ConnectionPool, project_id:str) -> None:

    with conn_pool.connection() as connection:
        with connection.cursor() as cur:
            refine_rails = f"""
              with projectbbox as 
                (   select 
                    (bbox -> 'xmax')::float xmax,
                    (bbox -> 'xmin')::float xmin,
                    (bbox -> 'ymax')::float ymax,
                    (bbox -> 'ymin')::float ymin 
                    from project
                    where project_id='{project_id}'
                )
                UPDATE rails r
                SET geom = ST_Intersection(r.geom, ST_MakeEnvelope (
                        p.xmin, p.ymin,
                        p.xmax, p.ymax,
                        4326))
                FROM projectbbox p where project_id='{project_id}';
            """
            cur.execute(refine_rails)
            connection.commit()

@lru_cache
def get_rails_from_db(conn_pool: ConnectionPool, projectId:str):
    with conn_pool.connection() as connection:
        get_rails_query =f''' select json_build_object(
                'type', 'FeatureCollection',
                'features', json_agg(ST_AsGeoJSON(rails.*)::json)
                )
                from rails
                where project_id = '{projectId}'
            ;
        '''
        rails = connection.execute(get_rails_query).fetchall()[0][0]
        return rails