ALTER TABLE comment 
ADD COLUMN IF NOT EXISTS quest_id INTEGER;
create table if not exists quests_user (quest_id INTEGER, user_id TEXT, project_id TEXT, fulfillment smallint);
drop table if exists quests;
create table quests (quest_id serial primary key NOT NULL, content json NOT NULL, type smallint, goal smallint, order_id smallint, project_id TEXT);
INSERT INTO quests (project_id, content, type, goal, order_id) VALUES ('0', '{"detailedDescription":"","title":"3 Orte die aufgewertet werden","description":"Markieren Sie mindestens 3 Orte, die durch die aktuelle Planung aufgewertet werden."}', '1', '3', '0');
INSERT INTO quests (project_id, content, type, goal, order_id) VALUES ('0', '{"detailedDescription":"","title":"3 Orte, die herabgestuft werden","description":"Markieren Sie mindestens 3 Orte, dessen Qualität durch die aktuelle Planung geschmälert wird."}', '1', '3', '1');
INSERT INTO quests (project_id, content, type, goal, order_id) VALUES ('0', '{"detailedDescription":"","title":"3 Orte, mit offenen Fragen","description":"Markieren Sie mindestens 3 Orte, bei denen Sie noch offene Fragen haben oder bei denen Sie etwas bestimmtes interessiert. "}', '1', '3', '2');
INSERT INTO quests (project_id, content, type, goal, order_id) VALUES ('DDN', '{"detailedDescription":"","title":"","description":"Schau dir den Planungsraum an und nutze das Linien-Werkzeug, um eine Route einzuzeichnen, die du regelmäßig benutzt, um dich im Planungsgebiet zu bewegen."}', '1', '2', '1');
INSERT INTO quests (project_id, content, type, goal, order_id) VALUES ('DDN', '{"detailedDescription":"","title":"","description":"Markiere mindestens 3 Orte, die durch die aktuelle Planung aufgewertet werden oder welche von einer der drei Varianten profitieren. Nutze die Kommentarfunktion um die Bereiche zu markieren. Erläutere kurz."}', '1', '3', '2');
INSERT INTO quests (project_id, content, type, goal, order_id) VALUES ('DDN', '{"detailedDescription":"","title":"","description":"Markiere nun mindestens 3 Orte, wo du Konfliktpotential durch die Planungsvarianten siehst oder wo noch etwas verbessert werden kann. Bitte beschreibe deine Auswahl."}', '1', '3', '3');
INSERT INTO quests (project_id, content, type, goal, order_id) VALUES ('DDN', '{"detailedDescription":"","title":"","description":"Markiere noch Orte, an welchen du die aktuelle Planung nicht verstehst und wo deiner Meinung nach Klärungsbedarf besteht."}', '1', '1', '4');
INSERT INTO quests (project_id, content, type, goal, order_id) VALUES ('DDN', '{"detailedDescription":"","title":"","description":"Hallo und Willkommen zur Mobilitätsbeteiligung in Mainz. Zum Ausbau des Straßenbahnnetzes soll eine neue Route in Mainz entstehen und es gibt schon jetzt die Möglichkeit Feedback und Ideen zur angedachten Planung einzureichen."}', '1', '1', '0');

