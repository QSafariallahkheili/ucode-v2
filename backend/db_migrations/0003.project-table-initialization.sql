drop table if exists project;
create table project (project_id TEXT unique, project_name TEXT, bbox jsonb, project_type TEXT NULL, project_goal TEXT null);
insert into project (project_id, project_name, bbox, project_type, project_goal) values ('0','Mainz', '{"xmin": 8.24287, "ymin": 49.992401, "xmax": 8.29617, "ymax": 50.018199}', 'transportation_planning', 'Die Mainzer Mobilität plant eine neue Straßenbahnstrecke vom Schillerplatz über das Höfchen in Richtung Mainzer Neustadt. Mit ihr soll die Altstadt künftig direkter mit dem bevölkerungsreichsten Mainzer Neustadt-Viertel verbunden werden. Es wurden drei Varianten einer Streckenführung erstellt, die Sie im folgenden kommentieren können.');


