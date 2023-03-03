insert into project (project_id, project_name, bbox) values 
('Hafencity','Hamburg Hafencity', '{"xmin": 9.976848, "ymin": 53.524465, "xmax": 10.033952, "ymax": 53.546335}'),
('San_Francisco','San Francisco', '{"xmin": -122.431817, "ymin": 37.777828, "xmax": -122.418183, "ymax": 37.784772}'),
('Vatican','Vatikanstadt', '{"xmin": 12.444708, "ymin": 41.8979, "xmax": 12.465092, "ymax": 41.9083}'),
('Central_Park','Central Park New York', '{"xmin": -73.994466, "ymin": 40.763297, "xmax": -73.934534, "ymax": 40.802703}'),
('Solar_One','Solar One: broken shape', '{"xmin": -73.974642, "ymin": 40.734426, "xmax": -73.973958, "ymax": 40.734774}'),
('Monaco','Monaco', '{"xmin": 7.406027, "ymin": 43.724257, "xmax": 7.444373, "ymax": 43.752543}')
    ON CONFLICT (project_id) DO NOTHING;
