drop table if exists project;
create table project (project_id TEXT unique, project_name TEXT, bbox jsonb, project_type TEXT NULL, project_goal TEXT null);
insert into project (project_id, project_name, bbox, project_type, project_goal) values ('0','Mainz', '{"xmin": 8.24287, "ymin": 49.992401, "xmax": 8.29617, "ymax": 50.018199}', 'transportation_planning', 'in this section the project goal can be set based on the project type and definition. It can be filled by the user in a provided from while initializing the project');


