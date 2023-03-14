create table if not exists rails (id SERIAL PRIMARY KEY, project_id TEXT, geom geometry(LINESTRING, 4326));
