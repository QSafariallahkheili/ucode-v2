import json

import requests
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from osmtogeojson import osmtogeojson

from buildings import create_building_polygons, persist_building_polygons
from db import (add_comment, add_drawn_line, add_fulfillment, connect,
                delete_comment_by_id, delete_comments, dislike_comment,
                drop_bike_polygon_table, drop_bike_table, drop_building_table,
                drop_driving_lane_table, drop_greenery_table,
                drop_sidewalk_polygon, drop_sidewalk_table,
                drop_traffic_signal_table, drop_tram_line_table,
                drop_tree_table, drop_water_table, get_bike_from_db,
                get_bike_lane_from_db, get_buildings_from_db, get_comments,
                get_driving_lane_from_db, get_driving_lane_polygon_from_db,
                get_filtered_comments, get_filtered_comments_with_status,
                get_greenery_from_db, get_project_specification_from_db,
                get_quests_and_fulfillment_from_db, get_quests_from_db,
                get_routes_from_db, get_sidewalk_from_db, get_table_names,
                get_traffic_signal_from_db, get_tram_line_from_db,
                get_trees_from_db, get_water_from_db, like_comment,
                prepare_quests_user_table, undislike_comment, unlike_comment,
                update_voting_status)
from db_migrations import run_database_migrations
from models import ProjectSpecification
from services.open_street_map import getDriveNetwork
from services.overpass import (interpreter, query_bike, query_building_parts,
                               query_building_with_hole, query_fountain,
                               query_greenery, query_serviceroad,
                               query_traffic_signals, query_tram_lines,
                               query_tree_row, query_trees, query_walk,
                               query_water)
from utils import sure_float

try:
    run_database_migrations()
except Exception as err:
    print("Could not run database migrations", err)


app = FastAPI()
origins = [
    "https://api.v2.urban-codesign.com",
    "https://v2.urban-codesign.com",
    "http://localhost",
    "http://localhost:8080"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

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
       
@app.get("/prepare-quests-user-table")
async def prepare_quests_user_table_api(projectId: str, userId:str):
    response = prepare_quests_user_table(projectId,userId)
    return response

@app.get("/add-quest-fulfillment")
async def add_fulfillment_api(questId: int, userId: str):
    response = add_fulfillment(questId, userId)
    return response
    
@app.post("/get-greenery-from-osm")
async def get_greenery_from_osm_api(request: Request):
    data = await request.json()
    projectId = data["projectId"] 
    drop_greenery_table(projectId)
    bbox = f"""{data["bbox"]["ymin"]},{data["bbox"]["xmin"]},{data["bbox"]["ymax"]},{data["bbox"]["xmax"]}"""
    tags = data["usedTagsForGreenery"]["tags"]
    _tags = ""
    for i in tags:
        _tags += "way.all[" + i.replace(":", "=") + "]" + ";\n"

    data_greenery = interpreter(query_greenery(bbox,_tags))

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
    return "gg"

@app.post("/get-greenery-from-db")
async def get_greenery_from_db_api(request: Request):
    data = await request.json()
    return get_greenery_from_db(data)


@app.post("/get-buildings-from-osm")
async def get_buildings_from_osm_api(request: Request):
    data = await request.json()
    projectId = data["projectId"]
    drop_building_table(projectId)
    bbox = f"""{data["bbox"]["ymin"]},{data["bbox"]["xmin"]},{data["bbox"]["ymax"]},{data["bbox"]["xmax"]}"""
    
    
    
    response_building = interpreter(query_building_parts(bbox))
    building_polygons = create_building_polygons(projectId,  response_building)
    persist_building_polygons(connect(), building_polygons)


    response_building_with_hole = interpreter(query_building_with_hole(bbox))
    for f in response_building_with_hole["elements"]:
        if "type" in f and f["type"] == "relation":
            if(f["members"][0]["role"] != "outer"):
                i = 0
                for x in f["members"]:
                    if x["role"] == "outer":
                        f["members"][0], f["members"][i] = f["members"][i],f["members"][0]
                        break
                    i += 1
                
    bhole = osmtogeojson.process_osm_json(response_building_with_hole)
    # print(bhole)
    connectionn = connect()
    cursorr = connectionn.cursor()
    insert_query_buildingg = """
        INSERT INTO building (project_id,wallcolor,wallmaterial, roofcolor,roofmaterial,roofshape,roofheight, height, floors, estimatedheight, amenity, geom) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s, ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326));
    """
    for f in bhole["features"]:
        
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
            cursorr.execute(
                    insert_query_buildingg,
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
                        json.dumps(f["geometry"]),
                    ),
            )
         
    connectionn.commit()
    cursorr.close()
    connectionn.close()


    # building refinement: identifing and deleting duplicated buildings and small overlapping building geometries
    
    connection = connect()
    cursor = connection.cursor()
    
    refinement_building_query = f"""
        with buildingone as (select * from building where project_id = '{projectId}' and st_isvalid(geom))

        delete from building where id in (
            select building.id from building, buildingone
            where building.project_id = '{projectId}' 
                and st_isvalid(building.geom) 
                and st_equals(building.geom, buildingone.geom) 
                and building.id <> buildingone.id
        );

        with buildingone as (select * from building where project_id = '{projectId}' and st_isvalid(geom))
            
        delete from building where id in (
            select building.id from building, buildingone 
            where building.project_id = '{projectId}' 
                and st_isvalid(building.geom) 
                and st_within(building.geom, buildingone.geom) 
                and building.id <> buildingone.id 
                and buildingone.estimatedheight >=building.estimatedheight);

    """
    
    cursor.execute(refinement_building_query)
    connection.commit()
    cursor.close()
    connection.close()
    

    return "fine"


@app.post("/get-buildings-from-db")
async def get_buildings_from_db_api(request: Request):
    data = await request.json()
    return get_buildings_from_db(data)

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
    drop_tree_table(projectId)
    bbox = f"""{data["bbox"]["ymin"]},{data["bbox"]["xmin"]},{data["bbox"]["ymax"]},{data["bbox"]["xmax"]}"""

    data_tree = interpreter(query_trees(bbox))

    connection = connect()
    cursor = connection.cursor()
    insert_query_tree = """
        INSERT INTO tree (project_id,geom) VALUES (%s,ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326));

    """
    for f in data_tree["elements"]:

        geom = json.dumps(f["geometry"])
        cursor.execute(insert_query_tree, (projectId,geom,))

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
        cursor.execute(insert_query_tree_row, (projectId,geom,))

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
    questId = data["questId"]
    
    routeId = None
    if data["routeId"] != None:
        routeId = data["routeId"]
    else: 
        routeId = "NULL"

    lng = sure_float(data["position"][0])
    lat = sure_float(data["position"][1])
    response = add_comment(userId,projectId,comment,lng,lat,questId,routeId)
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

#delete-comments
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
async def get_filtered_comments_with_status_api(projectId: str, userId:str):
    commentDataWithStatus = get_filtered_comments_with_status(projectId,userId)
    return commentDataWithStatus

@app.get("/get-filtered-comments")
async def get_filtered_comments_api(projectId: str, userId: str):
        return get_filtered_comments(projectId,userId)

@app.post("/get-filtered-comments")
async def get_filtered_comments_api(request: Request):
    data = await request.json()
    projectId = data["projectId"]
    userId = data["userId"]
    return get_filtered_comments(projectId,userId)


@app.get("/update-voting-status")
async def update_voting_status_api(commentId: str, userId:str, action:str):
    response = update_voting_status(commentId, userId, action)
    return response

@app.post("/like-comment")
async def like_comment_api(request: Request):
    data = await request.json()
    like_comment(data["id"],data["projectId"])
    return "added"


@app.post("/unlike-comment")
async def unlike_comment_api(request: Request):
    data = await request.json()
    unlike_comment(data["id"],data["projectId"])
    return "added"


@app.post("/dislike-comment")
async def dislike_comment_api(request: Request):
    data = await request.json()
    dislike_comment(data["id"],data["projectId"])
    return "added"


@app.post("/undislike-comment")
async def undislike_comment_api(request: Request):
    data = await request.json()
    undislike_comment(data["id"],data["projectId"])
    return "added"
  
@app.post("/get-driving-lane-from-osm")
async def get_driving_lane_from_osm_api(project_spec: ProjectSpecification):
    projectId = project_spec.projectId
    try:
        drop_driving_lane_table(projectId)
    except:
        print("Could not drop_driving_lane_table ")
    
    xmin = sure_float(project_spec.bbox.xmin)
    ymin = sure_float(project_spec.bbox.ymin)
    xmax = sure_float(project_spec.bbox.xmax)
    ymax = sure_float(project_spec.bbox.ymax) 
    try:
        road = getDriveNetwork(project_spec.bbox)
    except ValueError:
        raise HTTPException(
            status_code=412,
            detail="Found no graph nodes within the requested polygon"
        )
    #print(road)
    """
    mylist =[]
    for i in road['features']: 
        if i["properties"]["highway"] in mylist: 
            continue
        else:
            mylist.append(i["properties"]["highway"])
    print(mylist)
    """
    
    connection = connect()
    cursor = connection.cursor()

    insert_query_driving_lane= '''
        INSERT INTO driving_lane (project_id,lanes,length,maxspeed,width, highway, geom) VALUES (%s,%s,%s,%s,%s,%s, ST_SetSRID(st_astext(st_geomfromgeojson(%s)), 4326));

    '''

    insert_query_driving_lane_polygon= '''
        
        INSERT INTO driving_lane_polygon (project_id,lanes,length,maxspeed,width,highway, geom) VALUES (%s,%s,%s,%s,%s,%s,
        st_buffer(
            ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326)::geography,
            (%s::double precision)/2 ,
            'endcap=round join=round quad_segs=2')::geometry
        );
        

    '''
    for f in road['features']:
        #print(f)
        geom = json.dumps(f['geometry'])
        lanes=None
        if 'lanes' in f['properties']: lanes =f['properties']['lanes']
        length=None
        if 'length' in f['properties']: length =f['properties']['length']
        maxspeed=None
        if 'maxspeed' in f['properties']: maxspeed =f['properties']['maxspeed']

        highway=None
        if 'highway' in f['properties']: highway =f['properties']['highway']

        width=None
        if 'width' in f['properties'] and f['properties']["width"] is not None and isinstance(f['properties']["width"], str):
            width =f['properties']['width']
            width = sure_float(width)
        elif f['properties']["highway"]== 'primary':
            width =10
        elif f['properties']["highway"]== 'secondary' or f['properties']["highway"]== 'secondary_link':
            width =8
        elif f['properties']["highway"]== 'tertiary' or f['properties']["highway"]== 'tertiary_link':
            width =6
        elif f['properties']["highway"]== 'residential' or f['properties']["highway"]== 'living_street':
            width =4
        else:
            width =4
        cursor.execute(insert_query_driving_lane, (projectId,lanes,length,maxspeed,width,highway, geom,))
        cursor.execute(insert_query_driving_lane_polygon, (projectId,lanes,length,maxspeed,width,highway, geom,width))
    
    connection.commit()
    cursor.close()
    connection.close()

    connection = connect()
    cursor = connection.cursor()

    bbox = f"""{ymin},{xmin},{ymax},{xmax}"""
    data_serviceroad_osm = interpreter(query_serviceroad(bbox))
    data_serviceroad_geojson = osmtogeojson.process_osm_json(data_serviceroad_osm)
    for f in data_serviceroad_geojson["features"]:

        if f["geometry"]['type'] == "LineString":
           
            lanes=None
            if 'lanes' in f['properties']: lanes =f['properties']['lanes']
            length=None
            if 'length' in f['properties']: length =f['properties']['length']
            maxspeed=None
            if 'maxspeed' in f['properties']: maxspeed =f['properties']['maxspeed']
            highway=None
            if 'highway' in f['properties']: highway =f['properties']['highway']
            width = 2
            geom = json.dumps(f['geometry'])
            cursor.execute(insert_query_driving_lane_polygon, (projectId,lanes,length,maxspeed,width,highway, geom, width))

    connection.commit()
    cursor.close()
    connection.close()

    return "true"

@app.post("/get-driving-lane-from-db")
async def get_driving_lane_from_db_api(request: Request):
    projectId = await request.json()
    return {"lane": get_driving_lane_from_db(projectId), "polygon": get_driving_lane_polygon_from_db(projectId)}

#TH:add projectId to insert command
@app.post("/get-traffic-lights-from-osm")
async def get_traffic_lights_from_osm_api(request: Request):
    projectId ="0"
    drop_traffic_signal_table(projectId)
    data = await request.json()
    projectId = data["projectId"]
    drop_traffic_signal_table(projectId)
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
        cursor.execute(insert_query_traffic_signal, (geom, projectId, geom,))

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
    drop_water_table(projectId)
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
        cursor.execute(
        insert_query_water,
        (projectId,
        geom
        ))
    for f in data_water["features"]:
        if(f["geometry"]["type"]=="GeometryCollection"):
            polygon = {"type": "Polygon", "coordinates": []}
            outerPolygon = {"type": "Polygon", "coordinates": []}
            for g in f["geometry"]["geometries"]:
                if(g["type"]=="LineString"):
                    outerPolygon["coordinates"] += g["coordinates"]
                # if(g["type"]=="Polygon"):
                #     multipolygon["coordinates"].append(g["coordinates"])
            polygon["coordinates"] = [outerPolygon["coordinates"]]
            
            for g in f["geometry"]["geometries"]:
                if(g["type"]=="Polygon"):
                    polygon["coordinates"].append(g["coordinates"][0])

            # print(polygon)
            geom = json.dumps(polygon)
            cursor.execute(
            insert_query_water,
            (projectId,
            geom
            ))
        elif(f["geometry"]["type"]=="Polygon"):
            
            geom = json.dumps(f["geometry"])
            cursor.execute(
            insert_query_water,
            (projectId,
            geom
            ))
        else:
            print(f'''Some other type in Waterpolygons: {f["geometry"]["type"]}''')

    connection.commit()
    cursor.close()
    connection.close()
    return "gg"

@app.post("/get-tram-lines-from-osm")
async def get_tram_lines_from_osm_api(request: Request):
    
    data = await request.json()
    projectId = data["projectId"]
    drop_tram_line_table(projectId)
    bbox = f"""{data["bbox"]["ymin"]},{data["bbox"]["xmin"]},{data["bbox"]["ymax"]},{data["bbox"]["xmax"]}"""

    data_tram_lines = interpreter(query_tram_lines(bbox))
   
    connection = connect()
    cursor = connection.cursor()

    insert_query_tram_lane= '''
        INSERT INTO tram_line (project_id,lane_name,starts_from,arrives_to, geom) VALUES (%s,%s,%s,%s, ST_SetSRID(st_astext(st_geomfromgeojson(%s)), 4326));

    '''

    for elem in data_tram_lines["elements"]:
       
        lane_name=None
        if 'name' in elem["tags"]: lane_name = elem["tags"]['name']
        starts_from=None
        if 'from' in elem["tags"]: starts_from = elem["tags"]['from']
        arrives_to=None
        if 'to' in elem["tags"]: arrives_to = elem["tags"]['to']
        
        for geom in elem["geometry"]['geometries']:
            
            if geom["type"]=='LineString':
                tram_geom = json.dumps(geom)
                
                cursor.execute(insert_query_tram_lane, (projectId,lane_name,starts_from,arrives_to, tram_geom,))

    connection.commit()
    cursor.close()
    connection.close()
    
    
    connection = connect()
    cursor = connection.cursor()
    
    delete_station_geometries_query= '''

        delete from tram_line where ST_IsClosed(geom);
        
        delete FROM tram_line a
        WHERE NOT EXISTS 
        (SELECT 1 FROM tram_line b 
        WHERE a.id != b.id
        AND ST_Intersects(a.geom, b.geom) AND ST_Touches(a.geom, b.geom));

        update tram_line set geom = st_astext(st_transform(st_setsrid(ST_Collect(
            ST_OffsetCurve(st_transform(ST_SetSRID(geom, 4326), 26986), 0.4, 'quad_segs=4 join=mitre mitre_limit=2.2'),
            ST_OffsetCurve(st_transform(ST_SetSRID(geom, 4326), 26986), -0.4, 'quad_segs=4 join=mitre mitre_limit=2.2')
        ),26986),4326));

       
    '''
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
    drop_sidewalk_table(projectId)

    drop_sidewalk_polygon(projectId)
    
    ##### ############## overpass ###################
    bbox = f"""{data["bbox"]["ymin"]},{data["bbox"]["xmin"]},{data["bbox"]["ymax"]},{data["bbox"]["xmax"]}"""
    
    data_walk_osm = interpreter(query_walk(bbox))
    data_walk_geojson = osmtogeojson.process_osm_json(data_walk_osm)
    
    connection = connect()
    cursor = connection.cursor()

    insert_query_sidewalk= '''
        INSERT INTO sidewalk (project_id, highway, geom) VALUES (%s, %s, ST_SetSRID(st_astext(st_geomfromgeojson(%s)), 4326));
    '''
    
    for f in data_walk_geojson["features"]:
        if f["geometry"]['type'] == "LineString":
            highway=None
            if 'highway' in f['properties']: highway =f['properties']['highway']
            geom = json.dumps(f['geometry'])
            cursor.execute(insert_query_sidewalk, (projectId,highway, geom,))
            
    connection.commit()
    cursor.close()
    connection.close()
    
    connection = connect()
    cursor = connection.cursor()

    insert_query_driving_lane_polygon= '''
        
        INSERT INTO sidewalk_polygon(project_id, geom)
        SELECT project_id, st_buffer(
            ST_SetSRID(geom, 4326)::geography,
            1 ,
            'endcap=round join=round quad_segs=2')::geometry FROM sidewalk where project_id=%s;
    '''
    
    cursor.execute(insert_query_driving_lane_polygon, (projectId, ))
    
    connection.commit()
    cursor.close()
    connection.close()
    
    return "okk"

@app.post("/get-bike-from-osm")
async def get_bike_from_osm_api(request: Request):
    data = await request.json()
    projectId = data["projectId"]
    drop_bike_table(projectId)
    drop_bike_polygon_table(projectId)
    bbox = f"""{data["bbox"]["ymin"]},{data["bbox"]["xmin"]},{data["bbox"]["ymax"]},{data["bbox"]["xmax"]}"""

    data_bike = interpreter(query_bike(bbox))
        
    connection = connect()
    cursor = connection.cursor()

    insert_query_bike= '''
        INSERT INTO bike (project_id,oneway,highway,service_type,lanes, geom) VALUES (%s,%s,%s,%s,%s, ST_SetSRID(st_astext(st_geomfromgeojson(%s)), 4326));

    '''

    for elem in data_bike["elements"]:
       
        oneway=None
        if 'oneway' in elem["tags"]: oneway = elem["tags"]['oneway']
        highway=None
        if 'highway' in elem["tags"]: highway = elem["tags"]['highway']
        service_type=None
        if 'service_type' in elem["tags"]: service_type = elem["tags"]['service_type']
        lanes=None
        if 'lanes' in elem["tags"]: lanes = elem["tags"]['lanes']
        geom= json.dumps(elem['geometry'])
       
        cursor.execute(insert_query_bike, (projectId,oneway,highway,service_type,lanes, geom,))
    connection.commit()
    cursor.close()
    connection.close()

    connection = connect()
    cursor = connection.cursor()

    insert_query_bike_polygon= '''
    
        INSERT INTO bike_polygon(project_id, geom)
        SELECT project_id, st_buffer(
            ST_SetSRID(geom, 4326)::geography,
            0.5 ,
            'endcap=round join=round quad_segs=2')::geometry FROM bike where project_id=%s;

    '''
        
    cursor.execute(insert_query_bike_polygon, (projectId, ))

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

@app.get("/admin/clear-cache")
async def clear_cache():
    print("Cache cleared!")
    get_buildings_from_db_cache_stats = get_buildings_from_db.cache_info()
    get_greenery_from_db_cache_stats = get_greenery_from_db.cache_info()
    get_trees_from_db_cache_stats = get_trees_from_db.cache_info()
    get_driving_lane_from_db_cache_stats = get_driving_lane_from_db.cache_info()
    get_driving_lane_polygon_from_db_cache_stats = get_driving_lane_polygon_from_db.cache_info()
    get_traffic_signal_from_db_cache_stats =get_traffic_signal_from_db.cache_info()
    get_tram_line_from_db_cache_stats = get_tram_line_from_db.cache_info()
    get_water_from_db_cache_stats = get_water_from_db.cache_info()
    get_sidewalk_from_db_cache_stats = get_sidewalk_from_db.cache_info()
    get_bike_from_db_cache_stats = get_bike_from_db.cache_info()
    get_bike_lane_from_db_cache_stats = get_bike_lane_from_db.cache_info()
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
        "result": "Cache cleared"
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)