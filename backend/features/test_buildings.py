import json

from features.buildings import create_building_holes_polygons, create_building_polygons


def test_create_building_polygons(snapshot):
    with open("features/__fixtures__/building.json") as f:
        fixture = json.load(f)
        polygons = create_building_polygons("TestProjectId", fixture)
        assert polygons == snapshot


def test_create_building_holes_polygons(snapshot):

    with open("features/__fixtures__/building_holes.json") as f:
        fixture = json.load(f)
        polygons = create_building_holes_polygons("TestProjectId", fixture)
        assert polygons == snapshot
