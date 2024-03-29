import json

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from osmtogeojson import osmtogeojson

from features.buildings import (
    create_building_holes_polygons,
    create_building_polygons,
    get_buildings_from_db,
    persist_building_polygons,
    refine_persisted_buildings,
    transform_building_with_hole,
)
from features.driving_lane import (
    create_driving_lane_polygons,
    create_service_road_polygons,
    persist_driving_lane,
    persist_driving_lane_polygon,
)
from features.pedestrian_area import (
    create_pedestrian_area,
    persist_pedestrian_area_polygons,
    get_pedestrian_area_from_db,
)
from features.amenities import (
    create_amenities_polygons,
    persist_amenities_polygons,
    get_amenities_from_db,
)
from features.rails import (
    create_rails,
    persist_rails,
    refine_rails,
    get_rails_from_db
)
from db import (
    add_comment,
    add_drawn_line,
    add_fulfillment,
    connect,
    delete_comment_by_id,
    delete_comments,
    dislike_comment,
    get_bike_from_db,
    get_bike_lane_from_db,
    get_comments,
    get_driving_lane_from_db,
    get_driving_lane_polygon_from_db,
    get_filtered_comments,
    get_filtered_comments_with_status,
    get_greenery_from_db,
    get_project_specification_from_db,
    get_quests_and_fulfillment_from_db,
    get_quests_from_db,
    get_routes_from_db,
    get_sidewalk_from_db,
    get_traffic_signal_from_db,
    get_tram_line_from_db,
    get_trees_from_db,
    get_water_from_db,
    like_comment,
    prepare_quests_user_table,
    undislike_comment,
    unlike_comment,
    update_voting_status,
    generate_zebra_crossing_table,
    get_zebra_cross_from_db,
    update_project_starting_orientation,
    setup_new_project,
    delete_table_info_for_project,
    limit_features_to_project_bbox
)
from db_migrations import run_database_migrations
from models import ProjectSpecification, UpdateStartingOrientation
from services.open_street_map import getDriveNetwork
from services.overpass import (
    interpreter,
    query_bike,
    query_building_parts,
    query_building_with_hole,
    query_fountain,
    query_greenery,
    query_serviceroad,
    query_traffic_signals,
    query_tram_lines,
    query_tree_row,
    query_trees,
    query_walk,
    query_water,
    query_pedestrian_area,
    query_pedestrian_area_multipolygon,
    query_amenities,
    query_rails
)
from utils import sure_float
from repository.db import db_pool, get_table_names
from configuration import appConfig

try:
    run_database_migrations()
except Exception as err:
    print("Could not run database migrations", err)

app = FastAPI()
origins = [
    "https://api.v2.urban-codesign.com",
    "https://v2.urban-codesign.com",
    "https://demo.urban-codesign.com",
    "https://api.demo.urban-codesign.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.on_event("startup")
def open_pool():
    db_pool.open()


@app.on_event("shutdown")
def close_pool():
    db_pool.close()


@app.get("/")
async def root():
    try:
        table_names = get_table_names()
        if table_names:
            result = []
            for table in table_names:
                d = dict()
                d["id"] = table_names.index(table)
                d["name"] = table[0]
                result.append(d)
            subjects = json.dumps(result)
            return json.loads(subjects)
    except BaseException as err:
        print(f"Unexpected {err=}, {type(err)=}")
        raise HTTPException(status_code=500, detail=f"Something went wrong: {err}")


@app.get("/project-specification")
async def get_project_specification_from_db_api(projectId: str):
    return get_project_specification_from_db(projectId)


@app.post("/update-starting-orientation")
def update_project_starting_orientation_api(request: UpdateStartingOrientation):

    response = update_project_starting_orientation(
        db_pool, request.projectId, request.startingOrientation
    )
    return response


@app.get("/prepare-quests-user-table")
async def prepare_quests_user_table_api(projectId: str, userId: str):
    response = prepare_quests_user_table(projectId, userId)
    return response


@app.get("/add-quest-fulfillment")
async def add_fulfillment_api(questId: int, userId: str):
    response = add_fulfillment(questId, userId)
    return response


@app.post("/get-greenery-from-osm")
async def get_greenery_from_osm_api(request: Request):
    data = await request.json()
    projectId = data["projectId"]

    try:
        tableName = 'greenery'
        delete_table_info_for_project(projectId, tableName)
    except:
        print("Could not drop greenery table ")
    finally:
        get_greenery_from_db.cache_clear()

    bbox = f"""{data["bbox"]["ymin"]},{data["bbox"]["xmin"]},{data["bbox"]["ymax"]},{data["bbox"]["xmax"]}"""
    tags = data["usedTagsForGreenery"]["tags"]
    _tags = ""
    for i in tags:
        _tags += "way.all[" + i.replace(":", "=") + "]" + ";\n"

    data_greenery = interpreter(query_greenery(bbox, _tags))

    connection = connect()
    cursor = connection.cursor()
    insert_query_greenery = """
        INSERT INTO greenery (project_id,greentag, geom) VALUES (%s,%s, ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326));

    """
    for f in data_greenery["elements"]:
        f["geometry"]["type"] = "Polygon"
        f["geometry"]["coordinates"] = [f["geometry"]["coordinates"]]
        greentag = None
        for i in tags:
            if i.split(":")[0] in f["tags"]:
                greentag = f["tags"][i.split(":")[0]]
        if greentag == None:
            greentag = "notFound"
        geom = json.dumps(f["geometry"])

        # store_greenery_from_osm(greentag, geom)
        cursor.execute(
            insert_query_greenery,
            (
                projectId,
                greentag,
                geom,
            ),
        )

    connection.commit()
    cursor.close()
    connection.close()

    limit_features_to_project_bbox(
        db_pool,
        projectId,
        'greenery'
    )

    return "gg"


@app.post("/get-greenery-from-db")
async def get_greenery_from_db_api(request: Request):
    data = await request.json()
    return get_greenery_from_db(data)


@app.post("/get-buildings-from-osm")
async def get_buildings_from_osm_api(project_spec: ProjectSpecification):
    projectId = project_spec.projectId

    try:
        tableName = 'building'
        delete_table_info_for_project(projectId, tableName)
    except:
        print("Could not drop building table ")
    finally:
        get_buildings_from_db.cache_clear()

    response_building = interpreter(query_building_parts(project_spec.bbox))
    building_polygons = create_building_polygons(
        project_spec.projectId, response_building
    )
    persist_building_polygons(db_pool, building_polygons)

    response_building_with_hole = interpreter(
        query_building_with_hole(project_spec.bbox)
    )
    transform_building_with_hole(response_building_with_hole)

    bhole = osmtogeojson.process_osm_json(response_building_with_hole)
    building_holes_polygons = create_building_holes_polygons(projectId, bhole)
    persist_building_polygons(db_pool, building_holes_polygons)

    refine_persisted_buildings(db_pool, projectId)

    return "fine"


@app.get("/get-buildings-from-db")
def get_buildings_from_db_api(projectId: str):
    return get_buildings_from_db(db_pool, projectId)


@app.post("/get-quests-from-db")
async def get_quests_from_db_api(request: Request):
    projectId = await request.json()
    return get_quests_from_db(projectId)


@app.get("/get-quests-from-db")
async def get_quests_from_db_api(projectId: str):
    return get_quests_from_db(projectId)


##TH new quest request with userId in order to get the fullfillment-data from the user and provide it wit
@app.get("/get-quests-and-fulfillment-from-db")
async def get_quests_and_fulfillment_from_db_api(projectId: str, userId: str):
    return get_quests_and_fulfillment_from_db(projectId, userId)


@app.post("/get-trees-from-osm")
async def get_trees_from_osm_api(request: Request):
    data = await request.json()
    projectId = data["projectId"]
    
    try:
        tableName = 'tree'
        delete_table_info_for_project(projectId, tableName)
    except:
        print("Could not drop tree table ")
    finally:
        get_trees_from_db.cache_clear()

    bbox = f"""{data["bbox"]["ymin"]},{data["bbox"]["xmin"]},{data["bbox"]["ymax"]},{data["bbox"]["xmax"]}"""

    data_tree = interpreter(query_trees(bbox))

    connection = connect()
    cursor = connection.cursor()
    insert_query_tree = """
        INSERT INTO tree (project_id,geom) VALUES (%s,ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326));

    """
    for f in data_tree["elements"]:

        geom = json.dumps(f["geometry"])
        cursor.execute(
            insert_query_tree,
            (
                projectId,
                geom,
            ),
        )

    connection.commit()
    cursor.close()
    connection.close()

    data_tree_row = interpreter(query_tree_row(bbox))
    connection = connect()
    cursor = connection.cursor()
    insert_query_tree_row = """
        INSERT INTO tree (project_id,geom) VALUES (%s, st_setsrid((ST_DumpPoints(ST_AsText(ST_Segmentize(ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326)::geography, 10)))).geom,4326) );

    """
    for f in data_tree_row["elements"]:

        geom = json.dumps(f["geometry"])
        cursor.execute(
            insert_query_tree_row,
            (
                projectId,
                geom,
            ),
        )

    connection.commit()
    cursor.close()
    connection.close()
    return "ok"


@app.post("/get-trees-from-db")
async def get_trees_from_db_api(request: Request):
    projectId = await request.json()
    return get_trees_from_db(projectId)


@app.post("/add-comment")
async def add_comment_api(request: Request):
    data = await request.json()
    userId = data["userId"]
    projectId = data["projectId"]
    comment = data["comment"]

    routeId = None
    if data["routeId"] != None:
        routeId = data["routeId"]
    else:
        routeId = "NULL"

    questId = None
    if data["questId"] != None:
        questId = data["questId"]
    else:
        questId = "NULL"

    lng = sure_float(data["position"][0])
    lat = sure_float(data["position"][1])
    response = add_comment(userId, projectId, comment, lng, lat, questId, routeId)
    return response


@app.post("/add-drawn-line")
async def add_drawn_line_api(request: Request):
    data = await request.json()
    add_drawn_line(
        data["projectId"],
        data["comment"],
        data["width"],
        data["color"],
        json.dumps(data["geometry"]["features"][0]["geometry"]),
    )
    return "added"


# delete-comments
@app.get("/delete-comments")
async def delete_comments_api(projectId: str):
    return delete_comments(projectId)


@app.post("/get-comments")
async def get_comments_api(request: Request):
    data = await request.json()
    return get_comments(data)


@app.get("/get-comments")
async def get_comments_api(projectId: str):
    return get_comments(projectId)


@app.get("/get-filtered-comments-with-status")
async def get_filtered_comments_with_status_api(projectId: str, userId: str):
    commentDataWithStatus = get_filtered_comments_with_status(projectId, userId)
    return commentDataWithStatus


@app.get("/get-filtered-comments")
async def get_filtered_comments_api(projectId: str, userId: str):
    return get_filtered_comments(projectId, userId)


@app.post("/get-filtered-comments")
async def get_filtered_comments_api(request: Request):
    data = await request.json()
    projectId = data["projectId"]
    userId = data["userId"]
    return get_filtered_comments(projectId, userId)


@app.get("/update-voting-status")
async def update_voting_status_api(commentId: str, userId: str, action: str):
    response = update_voting_status(commentId, userId, action)
    return response


@app.post("/like-comment")
async def like_comment_api(request: Request):
    data = await request.json()
    like_comment(data["id"], data["projectId"])
    return "added"


@app.post("/unlike-comment")
async def unlike_comment_api(request: Request):
    data = await request.json()
    unlike_comment(data["id"], data["projectId"])
    return "added"


@app.post("/dislike-comment")
async def dislike_comment_api(request: Request):
    data = await request.json()
    dislike_comment(data["id"], data["projectId"])
    return "added"


@app.post("/undislike-comment")
async def undislike_comment_api(request: Request):
    data = await request.json()
    undislike_comment(data["id"], data["projectId"])
    return "added"


@app.post("/get-driving-lane-from-osm")
async def get_driving_lane_from_osm_api(project_spec: ProjectSpecification):
    projectId = project_spec.projectId
    try:
        tableName1 = 'driving_lane'
        tableName2 = 'driving_lane_polygon'

        delete_table_info_for_project(projectId, tableName1)
        delete_table_info_for_project(projectId, tableName2)
    except:
        print("Could not drop_driving_lane_table ")
    finally:
        get_driving_lane_from_db.cache_clear()
        get_driving_lane_polygon_from_db.cache_clear()

    xmin = sure_float(project_spec.bbox.xmin)
    ymin = sure_float(project_spec.bbox.ymin)
    xmax = sure_float(project_spec.bbox.xmax)
    ymax = sure_float(project_spec.bbox.ymax)
    try:
        road = getDriveNetwork(project_spec.bbox)
    except ValueError:
        raise HTTPException(
            status_code=412, detail="Found no graph nodes within the requested polygon"
        )
    driving_lane_polygons = create_driving_lane_polygons(projectId, road)
    persist_driving_lane(db_pool, driving_lane_polygons)
    persist_driving_lane_polygon(db_pool, driving_lane_polygons)

    bbox = f"""{ymin},{xmin},{ymax},{xmax}"""
    data_serviceroad_osm = interpreter(query_serviceroad(bbox))
    data_serviceroad_geojson = osmtogeojson.process_osm_json(data_serviceroad_osm)

    service_road_polygons = create_service_road_polygons(
        projectId, data_serviceroad_geojson
    )
    persist_driving_lane_polygon(db_pool, service_road_polygons)

    limit_features_to_project_bbox(
        db_pool,
        projectId,
        'driving_lane'
    )
    limit_features_to_project_bbox(
        db_pool,
        projectId,
        'driving_lane_polygon'
    )

    return "true"


@app.post("/get-driving-lane-from-db")
async def get_driving_lane_from_db_api(request: Request):
    projectId = await request.json()
    return {
        "lane": get_driving_lane_from_db(projectId),
        "polygon": get_driving_lane_polygon_from_db(projectId),
    }


# TH:add projectId to insert command
@app.post("/get-traffic-lights-from-osm")
async def get_traffic_lights_from_osm_api(request: Request):
    data = await request.json()
    projectId = data["projectId"]

    try:
        tableName = 'traffic_signal'
        delete_table_info_for_project(projectId, tableName)
    except:
        print("Could not drop traffic_signal table ")
    finally:
        get_traffic_signal_from_db.cache_clear()

    bbox = f"""{data["bbox"]["ymin"]},{data["bbox"]["xmin"]},{data["bbox"]["ymax"]},{data["bbox"]["xmax"]}"""

    data_traffic_signal = interpreter(query_traffic_signals(bbox))
    connection = connect()
    cursor = connection.cursor()
    insert_query_traffic_signal = """
        With closestpolygon AS
        (SELECT geom
        FROM driving_lane_polygon
        ORDER BY geom <-> (ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326))
        LIMIT 1)
        INSERT INTO traffic_signal (project_id,geom) VALUES 
        ( 
            %s,
            (select 
                ST_ClosestPoint(
                    ST_Boundary((select geom from closestpolygon)),
                    ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326)
                )
            )
        );

    """
    for f in data_traffic_signal["elements"]:

        geom = json.dumps(f["geometry"])
        cursor.execute(
            insert_query_traffic_signal,
            (
                geom,
                projectId,
                geom,
            ),
        )

    connection.commit()
    cursor.close()
    connection.close()
    return "ok"


@app.post("/get-traffic-signal-from-db")
async def get_traffic_lights_from_db_api(request: Request):
    projectId = await request.json()
    return get_traffic_signal_from_db(projectId)


@app.post("/get-routes-from-db")
async def get_routes_from_db_api(request: Request):
    projectId = await request.json()
    return get_routes_from_db(projectId)


@app.post("/get-water-from-db")
async def get_water_from_db_api(request: Request):
    projectId = await request.json()
    return get_water_from_db(projectId)


@app.post("/get-water-from-osm")
async def get_water_from_osm_api(request: Request):
    data = await request.json()
    projectId = data["projectId"]

    try:
        tableName = 'water'
        delete_table_info_for_project(projectId, tableName)
    except:
        print("Could not drop water table ")
    finally:
        get_water_from_db.cache_clear()

    bbox = f"""{data["bbox"]["ymin"]},{data["bbox"]["xmin"]},{data["bbox"]["ymax"]},{data["bbox"]["xmax"]}"""

    response_fountain = interpreter(query_fountain(bbox))
    response_water = interpreter(query_water(bbox))
    # print(response_water)

    data_fountain = osmtogeojson.process_osm_json(response_fountain)
    data_water = osmtogeojson.process_osm_json(response_water)
    # print(data_fountain)
    # print(data_water)
    connection = connect()
    cursor = connection.cursor()
    insert_query_water = """
        INSERT INTO water (project_id, geom) VALUES (%s, ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326));

    """

    for f in data_fountain["features"]:
        geom = json.dumps(f["geometry"])
        cursor.execute(insert_query_water, (projectId, geom))
    for f in data_water["features"]:
        if f["geometry"]["type"] == "GeometryCollection":
            polygon = {"type": "Polygon", "coordinates": []}
            outerPolygon = {"type": "Polygon", "coordinates": []}
            for g in f["geometry"]["geometries"]:
                if g["type"] == "LineString":
                    outerPolygon["coordinates"] += g["coordinates"]
                # if(g["type"]=="Polygon"):
                #     multipolygon["coordinates"].append(g["coordinates"])
            polygon["coordinates"] = [outerPolygon["coordinates"]]

            for g in f["geometry"]["geometries"]:
                if g["type"] == "Polygon":
                    polygon["coordinates"].append(g["coordinates"][0])

            # print(polygon)
            geom = json.dumps(polygon)
            cursor.execute(insert_query_water, (projectId, geom))
        elif f["geometry"]["type"] == "Polygon":

            geom = json.dumps(f["geometry"])
            cursor.execute(insert_query_water, (projectId, geom))
        else:
            print(f"""Some other type in Waterpolygons: {f["geometry"]["type"]}""")

    connection.commit()
    cursor.close()
    connection.close()
    
    limit_features_to_project_bbox(
        db_pool,
        projectId,
        'water'
    )

    return "gg"


@app.post("/get-tram-lines-from-osm")
async def get_tram_lines_from_osm_api(request: Request):

    data = await request.json()
    projectId = data["projectId"]
    
    try:
        tableName = 'tram_line'
        delete_table_info_for_project(projectId, tableName)
    except:
        print("Could not drop tram_line table ")
    finally:
        get_tram_line_from_db.cache_clear()

    

    bbox = f"""{data["bbox"]["ymin"]},{data["bbox"]["xmin"]},{data["bbox"]["ymax"]},{data["bbox"]["xmax"]}"""

    data_tram_lines = interpreter(query_tram_lines(bbox))

    connection = connect()
    cursor = connection.cursor()

    insert_query_tram_lane = """
        INSERT INTO tram_line (project_id,lane_name,starts_from,arrives_to, geom) VALUES (%s,%s,%s,%s, ST_SetSRID(st_astext(st_geomfromgeojson(%s)), 4326));

    """

    for elem in data_tram_lines["elements"]:

        lane_name = None
        if "name" in elem["tags"]:
            lane_name = elem["tags"]["name"]
        starts_from = None
        if "from" in elem["tags"]:
            starts_from = elem["tags"]["from"]
        arrives_to = None
        if "to" in elem["tags"]:
            arrives_to = elem["tags"]["to"]

        for geom in elem["geometry"]["geometries"]:

            if geom["type"] == "LineString":
                tram_geom = json.dumps(geom)

                cursor.execute(
                    insert_query_tram_lane,
                    (
                        projectId,
                        lane_name,
                        starts_from,
                        arrives_to,
                        tram_geom,
                    ),
                )

    connection.commit()
    cursor.close()
    connection.close()

    limit_features_to_project_bbox(
        db_pool,
        projectId,
        'tram_line'
    )

    connection = connect()
    cursor = connection.cursor()

    delete_station_geometries_query = f"""
        DELETE FROM tram_line WHERE ST_IsClosed(geom) AND project_id = '{projectId}';

        DELETE FROM tram_line a
        WHERE project_id = '{projectId}' AND NOT EXISTS 
        (SELECT 1 FROM tram_line b 
        WHERE a.id != b.id
        AND ST_Intersects(a.geom, b.geom) AND ST_Touches(a.geom, b.geom));

        UPDATE tram_line SET geom = ST_AsText(ST_Transform(ST_SetSRID(ST_Collect(
            ST_OffsetCurve(ST_Transform(ST_SetSRID(geom, 4326), 26986), 0.4, 'quad_segs=4 join=mitre mitre_limit=2.2'),
            ST_OffsetCurve(ST_Transform(ST_SetSRID(geom, 4326), 26986), -0.4, 'quad_segs=4 join=mitre mitre_limit=2.2')
        ),26986),4326))
        WHERE project_id = '{projectId}';
    """

    cursor.execute(delete_station_geometries_query)

    connection.commit()
    cursor.close()
    connection.close()


    return "tram lanes retrieved"


@app.post("/get-tram-line-from-db")
async def get_tram_line_from_db_api(request: Request):
    projectId = await request.json()
    return get_tram_line_from_db(projectId)


@app.post("/get-side-walk-from-osm")
async def get_side_walk_from_osm_api(request: Request):
    data = await request.json()

    projectId = data["projectId"]

    try:
        tableName1 = 'sidewalk'
        tableName2 = 'sidewalk_polygon'
        delete_table_info_for_project(projectId, tableName1)
        delete_table_info_for_project(projectId, tableName2)
    except:
        print("Could not drop sidewalk table ")
    finally:
        get_sidewalk_from_db.cache_clear()



    ##### ############## overpass ###################
    bbox = f"""{data["bbox"]["ymin"]},{data["bbox"]["xmin"]},{data["bbox"]["ymax"]},{data["bbox"]["xmax"]}"""

    data_walk_osm = interpreter(query_walk(bbox))
    data_walk_geojson = osmtogeojson.process_osm_json(data_walk_osm)

    connection = connect()
    cursor = connection.cursor()

    insert_query_sidewalk = """
        INSERT INTO sidewalk (project_id, highway, geom) VALUES (%s, %s, ST_SetSRID(st_astext(st_geomfromgeojson(%s)), 4326));
    """

    for f in data_walk_geojson["features"]:
        if f["geometry"]["type"] == "LineString":
            highway = None
            if "highway" in f["properties"]:
                highway = f["properties"]["highway"]
            geom = json.dumps(f["geometry"])
            cursor.execute(
                insert_query_sidewalk,
                (
                    projectId,
                    highway,
                    geom,
                ),
            )

    connection.commit()
    cursor.close()
    connection.close()

    connection = connect()
    cursor = connection.cursor()

    insert_query_sidewalk_polygon = """
        
        INSERT INTO sidewalk_polygon(project_id, geom)
        SELECT project_id, st_buffer(
            ST_SetSRID(geom, 4326)::geography,
            1 ,
            'endcap=round join=round quad_segs=2')::geometry FROM sidewalk where project_id=%s;
    """

    cursor.execute(insert_query_sidewalk_polygon, (projectId,))

    connection.commit()
    cursor.close()
    connection.close()

    limit_features_to_project_bbox(
        db_pool,
        projectId,
        'sidewalk_polygon'
    )

    return "okk"


@app.post("/get-bike-from-osm")
async def get_bike_from_osm_api(request: Request):
    data = await request.json()
    projectId = data["projectId"]
    
    try:
        tableName1 = 'bike'
        tableName2 = 'bike_polygon'

        delete_table_info_for_project(projectId, tableName1)
        delete_table_info_for_project(projectId, tableName2)
    except:
        print("Could not drop bike table ")
    finally:
        get_bike_from_db.cache_clear()
        get_bike_lane_from_db.cache_clear()

    bbox = f"""{data["bbox"]["ymin"]},{data["bbox"]["xmin"]},{data["bbox"]["ymax"]},{data["bbox"]["xmax"]}"""

    data_bike = interpreter(query_bike(bbox))

    connection = connect()
    cursor = connection.cursor()

    insert_query_bike = """
        INSERT INTO bike (project_id,oneway,highway,service_type,lanes, geom) VALUES (%s,%s,%s,%s,%s, ST_SetSRID(st_astext(st_geomfromgeojson(%s)), 4326));

    """

    for elem in data_bike["elements"]:

        oneway = None
        if "oneway" in elem["tags"]:
            oneway = elem["tags"]["oneway"]
        highway = None
        if "highway" in elem["tags"]:
            highway = elem["tags"]["highway"]
        service_type = None
        if "service_type" in elem["tags"]:
            service_type = elem["tags"]["service_type"]
        lanes = None
        if "lanes" in elem["tags"]:
            lanes = elem["tags"]["lanes"]
        geom = json.dumps(elem["geometry"])

        cursor.execute(
            insert_query_bike,
            (
                projectId,
                oneway,
                highway,
                service_type,
                lanes,
                geom,
            ),
        )
    connection.commit()
    cursor.close()
    connection.close()
    limit_features_to_project_bbox(
        db_pool,
        projectId,
        'bike'
    )
    connection = connect()
    cursor = connection.cursor()

    insert_query_bike_polygon = """
    
        INSERT INTO bike_polygon(project_id, geom)
        SELECT project_id, st_buffer(
            ST_SetSRID(geom, 4326)::geography,
            0.5 ,
            'endcap=round join=round quad_segs=2')::geometry FROM bike where project_id=%s;

    """

    cursor.execute(insert_query_bike_polygon, (projectId,))

    connection.commit()
    cursor.close()
    connection.close()

    return "okk"


@app.post("/get-sidewalk-from-db")
async def get_sidewalk_from_db_api(request: Request):
    projectId = await request.json()
    return get_sidewalk_from_db(projectId)


@app.post("/get-bike-from-db")
async def get_bike_from_db_api(request: Request):
    projectId = await request.json()
    bike_poly = get_bike_from_db(projectId)
    return bike_poly


@app.post("/get-amenities-from-osm")
async def get_amenities_from_osm_api(project_spec: ProjectSpecification):
    projectId = project_spec.projectId

    try:
        tableName = 'amenities'
        delete_table_info_for_project(projectId, tableName)
    except:
        print("Could not drop amenities table ")
    finally:
        get_amenities_from_db.cache_clear()

    response_amenities = osmtogeojson.process_osm_json(
        interpreter(query_amenities(project_spec.bbox))
    )
    amenity_polygons = create_amenities_polygons(
        project_spec.projectId, response_amenities
    )
    persist_amenities_polygons(db_pool, amenity_polygons)


    return "amenities from osm fine"


@app.get("/get-amenities-from-db")
def get_amenities_from_db_api(projectId: str):
    return get_amenities_from_db(db_pool, projectId)


@app.get("/admin/clear-cache")
async def clear_cache():
    print("Cache cleared!")
    get_buildings_from_db_cache_stats = get_buildings_from_db.cache_info()
    get_greenery_from_db_cache_stats = get_greenery_from_db.cache_info()
    get_trees_from_db_cache_stats = get_trees_from_db.cache_info()
    get_driving_lane_from_db_cache_stats = get_driving_lane_from_db.cache_info()
    get_driving_lane_polygon_from_db_cache_stats = (
        get_driving_lane_polygon_from_db.cache_info()
    )
    get_traffic_signal_from_db_cache_stats = get_traffic_signal_from_db.cache_info()
    get_tram_line_from_db_cache_stats = get_tram_line_from_db.cache_info()
    get_water_from_db_cache_stats = get_water_from_db.cache_info()
    get_sidewalk_from_db_cache_stats = get_sidewalk_from_db.cache_info()
    get_bike_from_db_cache_stats = get_bike_from_db.cache_info()
    get_bike_lane_from_db_cache_stats = get_bike_lane_from_db.cache_info()
    get_amenities_from_db_cache_stats = get_amenities_from_db.cache_info()
    get_zebra_cross_from_db_cache_stats = get_zebra_cross_from_db.cache_info()
    get_pedestrian_area_from_db_cache_stats = get_pedestrian_area_from_db.cache_info()
    get_rails_from_db_cache_stats =get_rails_from_db.cache_info()
    get_buildings_from_db.cache_clear()
    get_greenery_from_db.cache_clear()
    get_trees_from_db.cache_clear()
    get_driving_lane_from_db.cache_clear()
    get_driving_lane_polygon_from_db.cache_clear()
    get_traffic_signal_from_db.cache_clear()
    get_tram_line_from_db.cache_clear()
    get_water_from_db.cache_clear()
    get_sidewalk_from_db.cache_clear()
    get_bike_from_db.cache_clear()
    get_bike_lane_from_db.cache_clear()
    get_amenities_from_db.cache_clear()
    get_zebra_cross_from_db.cache_clear()
    get_pedestrian_area_from_db.cache_clear()
    get_rails_from_db.cache_clear()
    result = {
        "get_buildings_from_db_cache_stats": get_buildings_from_db_cache_stats,
        "get_greenery_from_db_cache_stats": get_greenery_from_db_cache_stats,
        "get_trees_from_db_cache_stats": get_trees_from_db_cache_stats,
        "get_driving_lane_from_db_cache_stats": get_driving_lane_from_db_cache_stats,
        "get_driving_lane_polygon_from_db_cache_stats": get_driving_lane_polygon_from_db_cache_stats,
        "get_traffic_signal_from_db_cache_stats": get_traffic_signal_from_db_cache_stats,
        "get_tram_line_from_db_cache_stats": get_tram_line_from_db_cache_stats,
        "get_water_from_db_cache_stats": get_water_from_db_cache_stats,
        "get_sidewalk_from_db_cache_stats": get_sidewalk_from_db_cache_stats,
        "get_bike_from_db_cache_stats": get_bike_from_db_cache_stats,
        "get_bike_lane_from_db_cache_stats": get_bike_lane_from_db_cache_stats,
        "get_amenities_from_db_cache_stats": get_amenities_from_db_cache_stats,
        "get_zebra_cross_from_db_cache_stats": get_zebra_cross_from_db_cache_stats,
        " get_pedestrian_area_from_db_cache_stats": get_pedestrian_area_from_db_cache_stats,
        "get_rails_from_db_cache_stats": get_rails_from_db_cache_stats,
        "result": "Cache cleared",
    }
    #    print(result)
    return result


@app.post("/get-bike-lanes-from-db")
async def get_bike_lanes_from_db_api(request: Request):
    projectId = await request.json()
    bike_lanes = get_bike_lane_from_db(projectId)
    return bike_lanes


@app.post("/delete-comment-by-id")
async def delete_comment_by_id_api(request: Request):
    data = await request.json()
    orderId = delete_comment_by_id(data["commentId"])
    return orderId


@app.post("/get-pedestrian-area-from-osm")
async def get_pedestrian_area_from_osm_api(project_spec: ProjectSpecification):

    try:
        tableName = 'pedestrian_area'
        delete_table_info_for_project(project_spec.projectId, tableName)
    except:
        print("Could not drop pedestrian_area table ")
    finally:
        get_pedestrian_area_from_db.cache_clear()

    pedestrian_area_data = interpreter(query_pedestrian_area(project_spec.bbox))
    data_pedestrian_area_geojson = osmtogeojson.process_osm_json(pedestrian_area_data)
    pedestrian_area_polygons = create_pedestrian_area(
        project_spec.projectId, data_pedestrian_area_geojson
    )
    persist_pedestrian_area_polygons(db_pool, pedestrian_area_polygons)

    pedestrian_area_data_multipolygon = interpreter(
        query_pedestrian_area_multipolygon(project_spec.bbox)
    )
    data_pedestrian_area_multipolygon_geojson = osmtogeojson.process_osm_json(
        pedestrian_area_data_multipolygon
    )
    pedestrian_area_multipolygons = create_pedestrian_area(
        project_spec.projectId, data_pedestrian_area_multipolygon_geojson
    )
    persist_pedestrian_area_polygons(db_pool, pedestrian_area_multipolygons)


    return "ok"


@app.post("/get-pedestrian-area-from-db")
async def get_pedestrian_are_from_db_api(request: Request):
    projectId = await request.json()
    return get_pedestrian_area_from_db(db_pool, projectId)


@app.post("/generate-zebra-crossing-table")
async def generate_zebra_crossing_table_api(request: Request):
    data = await request.json()
    projectId = data["projectId"]

    try:
        tableName = 'zebra_crossing'
        delete_table_info_for_project(projectId, tableName)
    except:
        print("Could not drop zebra_crossing table")
    finally:
        get_zebra_cross_from_db.cache_clear()

    generate_zebra_crossing_table(projectId)
    return "orderId"


@app.post("/get-zebra-cross-from-db")
async def get_zebra_crossing_from_db_api(request: Request):
    projectId = await request.json()
    zebra_crossing = get_zebra_cross_from_db(projectId)
    return zebra_crossing


@app.post("/setup_new_project")
async def setup_new_project_api(request: Request):
    api_key = request.headers.get("X-API-KEY")
    if api_key == appConfig["apiKey"]:
        data = await request.json()
        return setup_new_project(data)
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect API key",
        )

@app.post("/get-rails-from-osm")
async def get_rails_from_osm_api(project_spec: ProjectSpecification):

    try:
        tableName = 'rails'
        delete_table_info_for_project(project_spec.projectId, tableName)
    except:
        print("Could not drop rails table ")
    finally:
        get_rails_from_db.cache_clear()

    rails_data = interpreter(query_rails(project_spec.bbox))
    rails_data_geojson = osmtogeojson.process_osm_json(rails_data)

    rail_geometries = create_rails(
        project_spec.projectId, rails_data_geojson
    )
    persist_rails(db_pool, rail_geometries)
    
    limit_features_to_project_bbox(
        db_pool,
        project_spec.projectId,
        'rails'
    )
    
    return "alright"

@app.post("/get-rails-from-db")
async def get_rails_from_db_api(request: Request):
    projectId = await request.json()
    return get_rails_from_db(db_pool, projectId)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
