from functools import lru_cache
import json
from dataclasses import dataclass
from typing import Any, Dict, List
from psycopg_pool import ConnectionPool
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


def persist_building_polygons(
    conn_pool: ConnectionPool, building_polygons: List[BuildingPolygons]
):
    with conn_pool.connection() as connection:
        with connection.cursor() as cur:
            insert_query_building = """
                INSERT INTO building (project_id,wallcolor,wallmaterial, roofcolor,roofmaterial,roofshape,roofheight, height, floors, estimatedheight, amenity, geom) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s, ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326));
            """
            cur.executemany(insert_query_building, building_polygons)
            # batching doesn't bare much performance differences here because of the GIS operations involved
            # ps2.execute_batch(cursor, insert_query_building, building_polygons)
            connection.commit()

def refine_persisted_buildings(conn_pool: ConnectionPool, project_id:str) -> None:
    # building refinement: identifing and deleting duplicated buildings and small overlapping building geometries
    
    with conn_pool.connection() as connection:
        refinement_building_query = f"""
            with buildingone as (select * from building where project_id = '{project_id}' and st_isvalid(geom))

            delete from building where id in (
                select building.id from building, buildingone
                where building.project_id = '{project_id}' 
                    and st_isvalid(building.geom) 
                    and st_equals(building.geom, buildingone.geom) 
                    and building.id <> buildingone.id
            );

            with buildingone as (select * from building where project_id = '{project_id}' and st_isvalid(geom))
                
            delete from building where id in (
                select building.id from building, buildingone 
                where building.project_id = '{project_id}' 
                    and st_isvalid(building.geom) 
                    and st_within(building.geom, buildingone.geom) 
                    and building.id <> buildingone.id 
                    and buildingone.estimatedheight >=building.estimatedheight);

        """
        
        connection.execute(refinement_building_query)


def create_building_holes_polygons(project_id: str, data_building:Dict) -> List[BuildingPolygons]:
    result = []
    for f in data_building["features"]:
            
            if "type" in f["properties"] and f["properties"]["type"] == "multipolygon":
                
                wallcolor = None
                if "building:colour" in f["properties"]:
                    wallcolor = f["properties"]["building:colour"]
                wallmaterial = None
                if "building:material" in f["properties"]:
                    wallmaterial = f["properties"]["building:material"]
                roofcolor = None
                if "roof:colour" in f["properties"]:
                    roofcolor = f["properties"]["roof:colour"]
                roofmaterial = None
                if "roof:material" in f["properties"]:
                    roofmaterial = f["properties"]["roof:material"]
                roofshape = None
                if "roof:shape" in f["properties"]:
                    roofshape = f["properties"]["roof:shape"]
                roofheight = None
                if "roof:height" in f["properties"]:
                    roofheight = f["properties"]["roof:height"]
                    if "," in roofheight:
                        roofheight = roofheight.replace(",", ".")
                height = None
                if "height" in f["properties"]:
                    height = f["properties"]["height"]
                    height = sure_float(height)
                floors = None
                if "building:levels" in f["properties"]:
                    floors = f["properties"]["building:levels"]
                    floors = sure_float(floors)

                estimatedheight = None
                if height is not None:
                    estimatedheight = sure_float(height)
                elif floors is not None:
                    estimatedheight = sure_float(floors) * 3.5
                else:
                    estimatedheight = 15
                amenity = None
                if "amenity" in f["properties"]:
                    amenity = f["properties"]["amenity"]  
                tpl = tuple(    
                        (
                            project_id,
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
                            json.dumps(f["geometry"]),
                        ),
                )
                result.append(tpl)

    return result

@lru_cache
def get_buildings_from_db(conn_pool: ConnectionPool, projectId:str):
    with conn_pool.connection() as connection:
        get_building_query =f''' select json_build_object(
                'type', 'FeatureCollection',
                'features', json_agg(ST_AsGeoJSON(building.*)::json)
                )
                from building
                where project_id = '{projectId}'
            ;
        '''
        building = connection.execute(get_building_query).fetchall()[0][0]
        return building
    
def transform_building_with_hole(response_building_with_hole:Dict):
    for f in response_building_with_hole["elements"]:
        if "type" in f and f["type"] == "relation":
            if(f["members"][0]["role"] != "outer"):
                i = 0
                for x in f["members"]:
                    if x["role"] == "outer":
                        f["members"][0], f["members"][i] = f["members"][i],f["members"][0]
                        break
                    i += 1