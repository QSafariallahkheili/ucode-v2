drop table if exists amenities;
create table if not exists amenities (id SERIAL PRIMARY KEY, project_id TEXT, building_id TEXT, estimatedheight FLOAT(4), amenity TEXT, geom geometry(Geometry, 4326));
