CREATE INDEX IF NOT EXISTS idx_bike_geom ON bike USING gist (geom);
CREATE INDEX IF NOT EXISTS idx_driving_lane_polygon_geom ON driving_lane_polygon USING gist (geom);
CREATE INDEX IF NOT EXISTS idx_sidewalk_geom ON sidewalk USING gist (geom);
CREATE INDEX IF NOT EXISTS idx_traffic_signal_geom ON traffic_signal USING gist (geom);