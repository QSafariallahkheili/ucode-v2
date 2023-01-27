import pytest
from overpass import interpreter

from models import BoundingBox
from services.overpass import (
    query_bike,
    query_building_parts,
    query_building_with_hole,
    query_fountain,
    query_greenery,
    query_serviceroad,
    query_traffic_signals,
    query_tram_lines,
    query_tree_row,
    query_trees,
    query_walk,
    query_water,
)

HAMBURG_BBOX = BoundingBox(10.005326, 53.539938, 10.008459, 53.541302)


def test_interpreter_wrong_input_raises_retry_error():
    with pytest.raises(ConnectionError):
        assert interpreter("bam") == True


def test_interpreter(snapshot):
    query = query_building_parts(HAMBURG_BBOX)
    result = interpreter(query)
    assert result["elements"] == snapshot


def test_query_building_parts(snapshot):
    assert query_building_parts(HAMBURG_BBOX) == snapshot


def test_query_building_with_hole(snapshot):
    assert query_building_with_hole(HAMBURG_BBOX) == snapshot


def test_query_trees(snapshot):
    assert query_trees(HAMBURG_BBOX) == snapshot


def test_query_tree_row(snapshot):
    assert query_tree_row(HAMBURG_BBOX) == snapshot


def test_query_serviceroad(snapshot):
    assert query_serviceroad(HAMBURG_BBOX) == snapshot


def test_query_traffic_signals(snapshot):
    assert query_traffic_signals(HAMBURG_BBOX) == snapshot


def test_query_greenery(snapshot):
    assert (
        query_greenery(HAMBURG_BBOX, "way.all[natural=wood];way.all[landuse=meadow]")
        == snapshot
    )


def test_query_fountain(snapshot):
    assert query_fountain(HAMBURG_BBOX) == snapshot


def test_query_water(snapshot):
    assert query_water(HAMBURG_BBOX) == snapshot


def test_query_walk(snapshot):
    assert query_walk(HAMBURG_BBOX) == snapshot


def test_query_tram_lines(snapshot):
    assert query_tram_lines(HAMBURG_BBOX) == snapshot


def test_query_bike(snapshot):
    assert query_bike(HAMBURG_BBOX) == snapshot
