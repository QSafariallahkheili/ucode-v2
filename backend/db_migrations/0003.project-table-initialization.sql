drop table if exists project;
create table project (project_id TEXT unique, project_name TEXT, bbox jsonb, project_type TEXT NULL);
insert into project (project_id, project_name, bbox, project_type) values ('0','Mainz', '{"xmin": 8.24287, "ymin": 49.992401, "xmax": 8.29617, "ymax": 50.018199}', 'transportation_planning');


