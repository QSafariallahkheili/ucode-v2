from functools import lru_cache

import psycopg2

from configuration import dbConfig


def connect():
  return psycopg2.connect(
    host=dbConfig['host'],
    port=dbConfig['port'], 
    dbname=dbConfig['dbname'], 
    user=dbConfig['user'], 
    password=dbConfig['password'])


# def get_buildings_from_osm(wallcolor,wallmaterial, roofcolor,roofmaterial,roofshape,roofheight, height, floors, estimatedheight, geom):
#   connection = connect()
#   cursor = connection.cursor()
  
#   insert_query_building= '''
#         INSERT INTO building (wallcolor,wallmaterial, roofcolor,roofmaterial,roofshape,roofheight, height, floors, estimatedheight, geom) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s, ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326));

#   '''
#   cursor.execute(insert_query_building, (wallcolor,wallmaterial, roofcolor,roofmaterial,roofshape,roofheight, height, floors, estimatedheight, geom,))

#   connection.commit()
#   cursor.close()
#   connection.close()
#   return "ok"


def add_comment(userId, projectId, comment, lng, lat, questId,routeId):

  connection = connect()
  cursor = connection.cursor()
  
  insert_query_comment= f'''
    INSERT INTO comment (user_id,project_id,comment, geom, quest_id,route_id) VALUES ('{userId}','{projectId}','{comment}', ST_SetSRID(ST_MakePoint({lng}, {lat}), 4326),'{questId}',{routeId});

  '''
  cursor.execute(insert_query_comment)
  connection.commit()
  cursor.close()
  connection.close()

  if int(questId) > 0:
    return add_fulfillment(questId, userId)


def add_fulfillment(questId, userId):
  connection = connect()
  cursor = connection.cursor()
  insert_query_quests_fulfillment= f'''  
    update quests_user set fulfillment = fulfillment + 1 where quest_id='{questId}' and user_id='{userId}';
  '''
  cursor.execute(insert_query_quests_fulfillment)

  get_fulfillment_value = f'''  
    select fulfillment from quests_user where quest_id='{questId}' and user_id='{userId}';
  '''
  cursor.execute(get_fulfillment_value)
  updated_fulfillment_tuple = cursor.fetchall()
  connection.commit()
  cursor.close()
  connection.close()  
  updated_fulfillment =  updated_fulfillment_tuple[0][0]
  return updated_fulfillment


@lru_cache
def get_greenery_from_db(projectId):
  connection = connect()
  cursor = connection.cursor()
  get_greenery_query =f''' select json_build_object(
        'type', 'FeatureCollection',
        'features', json_agg(ST_AsGeoJSON(greenery.*)::json)
        )
        from greenery where project_id = '{projectId}'
      ;
  '''
  cursor.execute(get_greenery_query)
  greenery = cursor.fetchall()[0][0]
  cursor.close()
  connection.close()
  return greenery

@lru_cache
def get_trees_from_db(projectId):
  connection = connect()
  cursor = connection.cursor()
  get_trees_query =f''' select json_build_object(
        'type', 'FeatureCollection',
        'features', json_agg(ST_AsGeoJSON(tree.*)::json)
        )
        from tree where project_id = '{projectId}'
      ;
  '''
  cursor.execute(get_trees_query)
  trees = cursor.fetchall()[0][0]
  cursor.close()
  connection.close()
  return trees


def add_drawn_line(projectId,comment, width, color, geom):
  connection = connect()
  cursor = connection.cursor()
  
  insert_query_drawn_line= '''
    INSERT INTO drawnline (project_id, comment, width, color, geom) VALUES (%s,%s,%s, ST_SetSRID(st_astext(st_geomfromgeojson(%s)), 4326));

  '''
  cursor.execute(insert_query_drawn_line, (projectId, comment, width, color, geom,))
  connection.commit()
  cursor.close()
  connection.close()

def delete_comments(projectId):
  connection = connect()
  cursor = connection.cursor()
  delete_comments_query =f''' delete from comment where project_id='{projectId}';'''
  cursor.execute(delete_comments_query)
  connection.commit()
  cursor.close()
  connection.close()

def get_comments(projectId):
  connection = connect()
  cursor = connection.cursor()
  get_comment_query =f''' select json_build_object(
        'type', 'FeatureCollection',
        'features', json_agg(ST_AsGeoJSON(comment.*)::json)
        )
        from comment where project_id='{projectId}'
      ;
  '''
  cursor.execute(get_comment_query)
  comments = cursor.fetchall()[0][0]  
  cursor.close()
  connection.close
  return comments


def get_filtered_comments_with_status(projectId,userId):
  connection = connect()
  cursor = connection.cursor()

  get_comment_query =f''' 
  select json_build_object('type', 'FeatureCollection','features', json_agg(ST_AsGeoJSON(r.*)::json)) FROM 
  (SELECT  comment.*, comment_voting.voting_status, routes.color 
  FROM comment
  LEFT JOIN comment_voting
  ON comment.id = comment_voting.comment_id AND comment.project_id='{projectId}' AND comment_voting.user_id='{userId}'
  LEFT JOIN routes ON routes.id=comment.route_id where comment.project_id='{projectId}'
  ) r;
  '''
  cursor.execute(get_comment_query)
  comments = cursor.fetchall()[0][0]
  cursor.close()
  connection.close()

  if comments["features"] != None:  ## check, if there are comments
    for f in comments["features"]:
        author = f["properties"]["user_id"]
        if userId != author:
          f["properties"]["user_id"] = "anonymous"
        voting_status = f["properties"]["voting_status"]
        if voting_status == None:
          f["properties"]["voting_status"] = "undefined"
        
  return comments


def get_filtered_comments(projectId,userId):
  connection = connect()
  cursor = connection.cursor()
  get_comment_query =f''' select json_build_object(
        'type', 'FeatureCollection',
        'features', json_agg(ST_AsGeoJSON(comment.*)::json)
        )
        from comment where project_id='{projectId}'
      ;
  '''
  cursor.execute(get_comment_query)
  comments = cursor.fetchall()[0][0]

  for f in comments["features"]:
        currentUser = f["properties"]["user_id"]
        if str(userId) != str(currentUser):
          f["properties"]["user_id"] = "anonymous"

  cursor.close()
  connection.close()
  return comments


def update_comment_voting(comment_id, user_id, voting_status):
  
  connection = connect()
  cursor = connection.cursor()

  ## check, ob es überhaupt schon ein Voting zu diesem Kommentare gibt. wenn nicht, wird ein neuer erstellt, wenn ja, dann update

  get_votings_for_comment_query=f'''
    SELECT COUNT(voting_status) FROM comment_voting where comment_id = {comment_id} and user_id='{user_id}';
  '''
  cursor.execute(get_votings_for_comment_query)
  votings_for_comment_tuple = cursor.fetchall()
  votings_for_comment = int(votings_for_comment_tuple[0][0]) 
  if votings_for_comment < 1:
    set_voting_status_query =f''' INSERT INTO comment_voting (comment_id, user_id,voting_status) VALUES ('{comment_id}', '{user_id}','{voting_status}');'''
  else:
    set_voting_status_query =f''' UPDATE comment_voting SET voting_status = '{voting_status}' where comment_id = {comment_id} and user_id='{user_id}';'''
    
  cursor.execute(set_voting_status_query)
  connection.commit()
  cursor.close()
  connection.close()  


def update_voting_status(comment_id, user_id, action):

  ## check, which previous state the user has for the comment_id 

  connection = connect()
  cursor = connection.cursor()

  ## check, ob es überhaupt schon ein Voting zu diesem Kommentare gibt. wenn nicht, wird ein neuer erstellt, wenn ja, dann update

  get_previous_state_for_comment_query=f'''
    SELECT voting_status FROM comment_voting where comment_id = {comment_id} and user_id='{user_id}';
  '''
  cursor.execute(get_previous_state_for_comment_query)
  previous_state = cursor.fetchall()
  if len(previous_state) == 0: #TH# if there is no voting up to now, set the voting status to "undefined"
    previous_state = "undefined"
  else:
    previous_state = previous_state[0][0] 


  if previous_state == "undefined":
    
    if action == "like":
      result = {"status" : "like", "like" : 1, "dislike" : 0}
      like_comment(comment_id)
      update_comment_voting(comment_id, user_id, "like")

    elif action == "dislike":
      result = {"status" : "dislike", "like" : 0, "dislike" : 1}
      dislike_comment(comment_id)
      update_comment_voting(comment_id, user_id, "dislike")
    else:
      result = "Error"

  elif previous_state == "like":
	  
    if action == "like":
      result = {"status" : "undefined", "like" : -1, "dislike" : 0}
      unlike_comment(comment_id)
      update_comment_voting(comment_id, user_id, "undefined")

    elif action == "dislike":
      result = {"status" : "dislike", "like" : -1, "dislike" : 1}
      dislike_comment(comment_id)
      unlike_comment(comment_id)
      update_comment_voting(comment_id, user_id, "dislike")
    else:
      result = "Error"
	 
  elif previous_state == "dislike":
	
    if action == "like":
      result = {"status" : "like", "like" : 1, "dislike" : -1}
      like_comment(comment_id)
      undislike_comment(comment_id)
      update_comment_voting(comment_id, user_id, "like")

      
    elif action == "dislike":
      result = {"status" : "undefined", "like" : 0, "dislike" : -1}
      undislike_comment(comment_id)
      update_comment_voting(comment_id, user_id, "undefined")

    else:
      result = "Error"
  else:
    result = "Error"
   
  return result

def update_voting_status_v1(comment_id, user_id, action, previous_state):

  if previous_state == "undefined":
    
    if action == "like":
      result = {"status" : "like", "like" : 1, "dislike" : 0}
      like_comment(comment_id)
      update_comment_voting(comment_id, user_id, "like")

    elif action == "dislike":
      result = {"status" : "dislike", "like" : 0, "dislike" : 1}
      dislike_comment(comment_id)
      update_comment_voting(comment_id, user_id, "dislike")
    else:
      result = "Error"

  elif previous_state == "like":
	  
    if action == "like":
      result = {"status" : "undefined", "like" : -1, "dislike" : 0}
      unlike_comment(comment_id)
      update_comment_voting(comment_id, user_id, "undefined")

    elif action == "dislike":
      result = {"status" : "dislike", "like" : -1, "dislike" : 1}
      dislike_comment(comment_id)
      unlike_comment(comment_id)
      update_comment_voting(comment_id, user_id, "dislike")
    else:
      result = "Error"
	 
  elif previous_state == "dislike":
	
    if action == "like":
      result = {"status" : "like", "like" : 1, "dislike" : -1}
      like_comment(comment_id)
      undislike_comment(comment_id)
      update_comment_voting(comment_id, user_id, "like")

      
    elif action == "dislike":
      result = {"status" : "undefined", "like" : 0, "dislike" : -1}
      undislike_comment(comment_id)
      update_comment_voting(comment_id, user_id, "undefined")

    else:
      result = "Error"
  else:
    result = "Error"
   
  return result

def like_comment(commentid):
  connection = connect()
  cursor = connection.cursor()
  add_like_query =f''' UPDATE comment SET likes = likes + 1 where id = {commentid};'''
  cursor.execute(add_like_query, ())
  
  connection.commit()
  cursor.close()
  connection.close()
  return "ok"

def unlike_comment(commentid):
  connection = connect()
  cursor = connection.cursor()
  add_unlike_query =f''' UPDATE comment SET likes = likes - 1 where id = {commentid};'''
  cursor.execute(add_unlike_query, ())
  
  connection.commit()
  cursor.close()
  connection.close()
  return "ok"

def dislike_comment(commentid):
  connection = connect()
  cursor = connection.cursor()
  add_dislike_query =f''' UPDATE comment SET dislikes = dislikes + 1 where id = {commentid};'''
  cursor.execute(add_dislike_query, ())
  
  connection.commit()
  cursor.close()
  connection.close()
  return "ok"

def undislike_comment(commentid):
  connection = connect()
  cursor = connection.cursor()
  add_undislike_query =f''' UPDATE comment SET dislikes = dislikes - 1 where id = {commentid};'''
  cursor.execute(add_undislike_query, ())
  
  connection.commit()
  cursor.close()
  connection.close()
  return "ok"

# def init_driving_lane_table(): # Not used
#   connection = connect()
#   cursor = connection.cursor()
#   create_driving_lane_table_query =''' 
#         drop table if exists driving_lane;
#         drop table if exists driving_lane_polygon;
#         create table driving_lane (id SERIAL PRIMARY KEY, lanes text, length float, maxspeed text, width text null,highway text, geom geometry(LINESTRING, 4326));
#         create table driving_lane_polygon (id SERIAL PRIMARY KEY, lanes text, length float, maxspeed text, width text null,highway text, geom geometry(Geometry, 4326));
#   '''
#   cursor.execute(create_driving_lane_table_query)

#   connection.commit()
#   cursor.close()
#   connection.close()
#   return "ok"
@lru_cache
def get_driving_lane_from_db(projectId):
  connection = connect()
  cursor = connection.cursor()
  get_driving_lane_query =f''' select json_build_object(
        'type', 'FeatureCollection',
        'features', json_agg(ST_AsGeoJSON(driving_lane.*)::json)
        )
        from driving_lane where project_id = '{projectId}'
      ;
  '''
  cursor.execute(get_driving_lane_query)
  driving_lane = cursor.fetchall()[0][0]
  cursor.close()
  connection.close()
  return driving_lane

@lru_cache
def get_driving_lane_polygon_from_db(projectId):
  connection = connect()
  cursor = connection.cursor()
  get_driving_lane_polygon_query =f''' select json_build_object(
        'type', 'FeatureCollection',
        'features', json_agg(ST_AsGeoJSON(driving_lane_polygon.*)::json)
        )
        from driving_lane_polygon where project_id = '{projectId}'
      ;
  '''
  cursor.execute(get_driving_lane_polygon_query)
  driving_lane_polygon = cursor.fetchall()[0][0]
  cursor.close()
  connection.close()
  return driving_lane_polygon


def prepare_quests_user_table(projectId,userId):
  connection = connect()
  cursor = connection.cursor()

# 1. If and how many quests are defined for this project?

  get_quests_from_db_query=f'''
    SELECT COUNT(quest_id) FROM quests WHERE project_id='{projectId}';
  '''
  cursor.execute(get_quests_from_db_query)
  number_of_quests_tuple = cursor.fetchall()
  number_of_quests = int(number_of_quests_tuple[0][0]) 
  if number_of_quests < 1:
    return "No quests available for this project" 

# 2. Are there any quests with fulfimments stored for the current user?

  get_fulfillments_from_db_query=f'''
    SELECT COUNT(fulfillment) FROM quests_user WHERE user_id='{userId}' and project_id='{projectId}';
  '''
  cursor.execute(get_fulfillments_from_db_query)
  number_of_fulfillments_tuple = cursor.fetchall()
  number_of_fulfillments = int(number_of_fulfillments_tuple[0][0]) 

# 3. If there are no stored fulfillments, then create new rows with fulfillment = 0 

  if number_of_fulfillments < 1: 
    # jetzt die Tabelle mit den Questfulfillments updaten
    get_quests_from_db_query=f'''
      SELECT * FROM quests WHERE project_id='{projectId}';
      '''
    cursor.execute(get_quests_from_db_query)
    quests = cursor.fetchall()
    
    # iterate over quest list
    for f in quests:
      quest_id = int(f[0])
      add_quest_user_query = f'''
      insert into quests_user (quest_id, project_id, user_id,fulfillment) values ('{quest_id}','{projectId}','{userId}',0);
      '''
      cursor.execute(add_quest_user_query)
    
    feedback = "New entries created"
  else:
    feedback = "Entries existed before"

  connection.commit()
  cursor.close()
  connection.close()
  return feedback

def get_quests_from_db(projectId):
  connection = connect()
  cursor = connection.cursor()
  # get_quests_from_db_query=f'''
  # select * from quests where project_id = '{projectId}';
  # '''

  get_quests_from_db_query=f'''
  select json_build_object('quest_id', quest_id, 'content',content, 'type',type,'goal',goal, 'order_id', order_id, 'project_id',project_id) from quests where project_id = '{projectId}';
  '''
  cursor.execute(get_quests_from_db_query)
  quests = cursor.fetchall()
  ## BUG: die einzelnen quests sind doppelt indented: wieso?
  cursor.close()
  connection.close()
  return quests

#  Returns a JSON with the combined descritions of the quests for the current project and the fulfillemt values for the current user
# This is important for creating a UI qwhich shows the user, how many quests his still has to do 
def get_quests_and_fulfillment_from_db(projectId,userId):
  connection = connect()
  cursor = connection.cursor()
  get_quests_from_db_query=f'''
  select json_build_object('quest_id',quest_id, 'content',content,'type',type,'goal',goal,'order_id',order_id,'project_id',project_id) from quests where project_id = '{projectId}' order by order_id;
  '''
  cursor.execute(get_quests_from_db_query)
  quests = cursor.fetchall()
  get_fulfillment_query=f'''
    select quest_id,fulfillment from quests_user where user_id = '{userId}' and project_id='{projectId}';
    '''
  cursor.execute(get_fulfillment_query)
  fulfillment_tuple = cursor.fetchall()
  cursor.close()
  connection.close()

  fulfillment_dict= dict(fulfillment_tuple)
  
  counter = 0
  quest_with_fulfillment = {} 
  for f in quests:
    quest_entry= f[0]
    quest_with_fulfillment[counter] = quest_entry
    quest_id = int(quest_with_fulfillment[counter]["quest_id"])
    fulfillment_value = fulfillment_dict[quest_id] 
    quest_with_fulfillment[counter]["fulfillment"] = fulfillment_value
    counter = counter + 1

  return quest_with_fulfillment


def drop_greenery_table(projectId):
  connection = connect()
  cursor = connection.cursor()
  drop_greenery_table_query =f''' delete from greenery where project_id='{projectId}';'''
  cursor.execute(drop_greenery_table_query)
  connection.commit()
  cursor.close()
  connection.close()
  
def drop_building_table(projectId):
  connection = connect()
  cursor = connection.cursor()
  drop_building_table_query =f''' delete from building where project_id='{projectId}';'''
  cursor.execute(drop_building_table_query)
  connection.commit()
  cursor.close()
  connection.close()

def drop_tree_table(projectId):
  connection = connect()
  cursor = connection.cursor()
  drop_tree_table_query =f''' delete from tree where project_id='{projectId}';'''
  cursor.execute(drop_tree_table_query)
  connection.commit()
  cursor.close()
  connection.close()

def drop_driving_lane_table(projectId):
  connection = connect()
  cursor = connection.cursor()
  drop_driving_lane_table_query =f''' delete from driving_lane where project_id='{projectId}'; delete from driving_lane_polygon where project_id='{projectId}';'''
  cursor.execute(drop_driving_lane_table_query)
  connection.commit()
  cursor.close()
  connection.close()

def drop_traffic_signal_table(projectId):
  connection = connect()
  cursor = connection.cursor()
  drop_traffic_signal_table_query =f''' delete from traffic_signal where project_id='{projectId}';'''
  cursor.execute(drop_traffic_signal_table_query)
  connection.commit()
  cursor.close()
  connection.close()

def drop_tram_line_table(projectId):
  connection = connect()
  cursor = connection.cursor()
  drop_tram_line_table_query =f''' delete from tram_line where project_id='{projectId}';'''
  cursor.execute(drop_tram_line_table_query)
  connection.commit()
  cursor.close()
  connection.close()

def drop_water_table(projectId):
  connection = connect()
  cursor = connection.cursor()
  drop_water_table_query =f''' delete from water where project_id='{projectId}';'''
  cursor.execute(drop_water_table_query)
  connection.commit()
  cursor.close()
  connection.close()

def drop_sidewalk_table(projectId):
  connection = connect()
  cursor = connection.cursor()
  drop_sidewalk_table_query =f''' delete from sidewalk where project_id='{projectId}';'''
  cursor.execute(drop_sidewalk_table_query)
  connection.commit()
  cursor.close()
  connection.close()

def drop_sidewalk_polygon(projectId):
  connection = connect()
  cursor = connection.cursor()
  drop_sidewalk_polygon_query =f''' delete from sidewalk_polygon where project_id='{projectId}';'''
  cursor.execute(drop_sidewalk_polygon_query)
  connection.commit()
  cursor.close()
  connection.close()

def drop_bike_table(projectId):
  connection = connect()
  cursor = connection.cursor()
  drop_bike_query =f''' delete from bike where project_id='{projectId}';'''
  cursor.execute(drop_bike_query)
  connection.commit()
  cursor.close()
  connection.close()

def drop_bike_polygon_table(projectId):
  connection = connect()
  cursor = connection.cursor()
  drop_bike_polygon_query =f''' delete from bike_polygon where project_id='{projectId}';'''
  cursor.execute(drop_bike_polygon_query)
  connection.commit()
  cursor.close()
  connection.close()

def drop_amenities_table(projectId):
  connection = connect()
  cursor = connection.cursor()
  drop_amenities_table_query =f''' delete from amenities where project_id='{projectId}';'''
  cursor.execute(drop_amenities_table_query)
  connection.commit()
  cursor.close()
  connection.close()

@lru_cache
def get_traffic_signal_from_db(projectId):
  connection = connect()
  cursor = connection.cursor()
  get_traffic_signal_query =f''' select json_build_object(
        'type', 'FeatureCollection',
        'features', json_agg(ST_AsGeoJSON(traffic_signal.*)::json)
        )
        from traffic_signal where project_id = '{projectId}'
      ;
  '''
  cursor.execute(get_traffic_signal_query)
  traffic_signal = cursor.fetchall()[0][0]
  cursor.close()
  connection.close()
  return traffic_signal

def get_project_specification_from_db(projectId):
  connection = connect()
  cursor = connection.cursor()
  get_project_specification_from_db_query =f''' 
      select json_agg(project.*) from project where project_id = '{projectId}';
  '''
  cursor.execute(get_project_specification_from_db_query)
  bbox = cursor.fetchall()[0][0]
  cursor.close()
  connection.close()
  return bbox

def get_routes_from_db(projectId):
  connection = connect()
  cursor = connection.cursor()
  get_routes_query = f''' select json_build_object(
        'type', 'FeatureCollection',
        'features', json_agg(ST_AsGeoJSON(routes.*)::json)
        )
        from routes
        where project_id = '{projectId}'
      ;
  '''
  cursor.execute(get_routes_query)
  routes = cursor.fetchall()[0][0]
  cursor.close()
  connection.close()
  return routes

@lru_cache
def get_tram_line_from_db(projectId):
  connection = connect()
  cursor = connection.cursor()
  get_tram_line_query = f''' select json_build_object(
        'type', 'FeatureCollection',
        'features', json_agg(ST_AsGeoJSON(tram_line.*)::json)
        )
        from tram_line
        where project_id = '{projectId}'
      ;
  '''
  cursor.execute(get_tram_line_query)
  routes = cursor.fetchall()[0][0]
  cursor.close()
  connection.close()
  return routes

@lru_cache
def get_water_from_db(projectId):
  connection = connect()
  cursor = connection.cursor()
  get_routes_query = f''' select json_build_object(
        'type', 'FeatureCollection',
        'features', json_agg(ST_AsGeoJSON(water.*)::json)
        )
        from water
        where project_id = '{projectId}'
      ;
  '''
  cursor.execute(get_routes_query)
  routes = cursor.fetchall()[0][0]
  cursor.close()
  connection.close()
  return routes

@lru_cache
def get_sidewalk_from_db(projectId):
  connection = connect()
  cursor = connection.cursor()
  get_sidewalk_query = f''' select json_build_object(
        'type', 'FeatureCollection',
        'features', json_agg(ST_AsGeoJSON(sidewalk_polygon.*)::json)
        )
        from sidewalk_polygon
        where project_id = '{projectId}'
      ;
  '''
  cursor.execute(get_sidewalk_query)
  sidewalk = cursor.fetchall()[0][0]
  cursor.close()
  connection.close()
  return sidewalk

@lru_cache
def get_bike_from_db(projectId):
  connection = connect()
  cursor = connection.cursor()
  get_bike_query = f''' select json_build_object(
        'type', 'FeatureCollection',
        'features', json_agg(ST_AsGeoJSON(bike_polygon.*)::json)
        )
        from (
          select id, (ST_Dump(bike_polygon.geom)).geom::geometry(Polygon,4326) from bike_polygon where project_id = '{projectId}'
        ) as bike_polygon
        
      ;
  '''
  cursor.execute(get_bike_query)
  bike_lanes = cursor.fetchall()[0][0]
  cursor.close()
  connection.close()
  return bike_lanes

@lru_cache
def get_bike_lane_from_db(projectId):
  connection = connect()
  cursor = connection.cursor()
  get_bike_lane_query = f''' select json_build_object(
        'type', 'FeatureCollection',
        'features', json_agg(ST_AsGeoJSON(bike.*)::json)
        )
        from bike
        where project_id = '{projectId}'
      ;
  '''
  cursor.execute(get_bike_lane_query)
  lane = cursor.fetchall()[0][0]
  cursor.close()
  connection.close()
  return lane

def delete_comment_by_id(comment_id):
  connection = connect()
  cursor = connection.cursor()
  
  selectCommentData = f''' select user_id,quest_id from comment where id= '{comment_id}'
  '''
  cursor.execute(selectCommentData)
  commentData = cursor.fetchall()
  userId = commentData[0][0]
  questId = commentData[0][1]
  orderId = "ok" #TH only for testing, if no quest_id is there

  # if the comment belongs to a quest, the fulfillment of this quest is reduced
  if questId != None:
    subtract_fulfillment= f'''  
      update quests_user set fulfillment = fulfillment - 1 where quest_id='{questId}' and user_id='{userId}';
      '''
    cursor.execute(subtract_fulfillment)
    selectOrderId = f''' select order_id from quests where quest_id= '{questId}'
    '''
    cursor.execute(selectOrderId)
    orderId = cursor.fetchall()[0][0]

  delete_comment = f''' delete from comment where id= '{comment_id}'; '''
  cursor.execute(delete_comment)
  
  connection.commit()
  cursor.close()
  connection.close()
  return orderId

def drop_pedestrian_area_table(projectId):
  connection = connect()
  cursor = connection.cursor()
  drop_pedestrian_areatable__query =f''' delete from pedestrian_area where project_id='{projectId}';'''
  cursor.execute(drop_pedestrian_areatable__query)
  connection.commit()
  cursor.close()
  connection.close()

def drop_zebra_crossing_table(projectId):
  connection = connect()
  cursor = connection.cursor()
  delete_zebra_crossing_query =f''' delete from zebra_crossing where project_id='{projectId}';'''
  cursor.execute(delete_zebra_crossing_query)
  connection.commit()
  cursor.close()
  connection.close()

def generate_zebra_crossing_table(projectId):
  connection = connect()
  cursor = connection.cursor()
  insert_zebra_crossing_query = f''' 
    with a as (select ST_collect(geom) as geom from sidewalk where st_isvalid(geom) and project_id='{projectId}'
    ),
    b as (select st_union(geom) as geom from driving_lane_polygon where project_id='{projectId}'
    ),
    c as (select ST_collect(geom) as geom from bike where st_isvalid(geom) and project_id='{projectId}'
    ),

    merged as (SELECT geom FROM a
    UNION 
    SELECT geom FROM c ),


    dumps as (select (st_dump(st_intersection(merged.geom, b.geom))).geom as geom from merged, b where st_intersects(merged.geom, b.geom) ),


    detected as (select ROW_NUMBER() OVER (ORDER BY dumps.geom) AS gid, dumps.geom from dumps, traffic_signal 
    where st_length(dumps.geom::geography)<14 and st_length(dumps.geom::geography)>2
    and 
    ST_DWithin(dumps.geom::geography,traffic_signal.geom::geography, 4) group by dumps.geom),




    firstoffset as (select detected.gid, st_transform(ST_OffsetCurve(st_transform(ST_SetSRID(geom, 4326), 26986), 1),4326) as geom  from detected),

    secondoffset as (select detected.gid, st_transform(ST_OffsetCurve(st_transform(ST_SetSRID(geom, 4326), 26986), -1),4326) as geom  from detected),


    snappedone as (select firstoffset.gid, st_setsrid((ST_DumpPoints(ST_AsText(ST_Segmentize(ST_SetSRID(geom, 4326)::geography, 0.9)))).geom,4326)  as geom from firstoffset),
    snappedsecond as (select secondoffset.gid, st_setsrid((ST_DumpPoints(ST_AsText(ST_Segmentize(ST_SetSRID(geom, 4326)::geography, 0.9)))).geom,4326)  as geom from secondoffset),



    generatedlines as (select snappedone.gid, st_makeline(
      snappedone.geom,
      st_closestpoint( snappedsecond.geom, snappedone.geom)) as geom from snappedone, snappedsecond  where snappedone.gid = snappedsecond.gid),
  

    stripes as (select st_buffer(geom::geography, 0.1, 'endcap=square') as geom from generatedlines where st_length(geom::geography)<1.99)

    insert into zebra_crossing (project_id, geom)
    select '{projectId}' as project_id, geom from stripes
  
  '''
  cursor.execute(insert_zebra_crossing_query)
  connection.commit()
  cursor.close()
  connection.close()

@lru_cache
def get_zebra_cross_from_db(projectId):
  connection = connect()
  cursor = connection.cursor()
  get_zebra_crossing_query = f''' select json_build_object(
        'type', 'FeatureCollection',
        'features', json_agg(ST_AsGeoJSON(zebra_crossing.*)::json)
        )
        from zebra_crossing
        where project_id = '{projectId}'
      ;
  '''
  cursor.execute(get_zebra_crossing_query)
  get_zebra = cursor.fetchall()[0][0]
  cursor.close()
  connection.close()
  return get_zebra