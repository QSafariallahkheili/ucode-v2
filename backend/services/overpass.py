from typing import Any

import requests
from tenacity import retry, stop, wait

from models import BoundingBox

OVERPASS_URL = "https://overpass-api.de/api/interpreter"


@retry(
    stop=stop.stop_after_attempt(3),
    wait=wait.wait_exponential(multiplier=1, min=3, max=7),
    reraise=True,
)
def interpreter(query: str) -> dict:
    overpass_request = requests.post(OVERPASS_URL, data=query)
    if overpass_request.status_code != 200:
        raise ConnectionError(overpass_request.reason)
    return overpass_request.json()


def query_building_parts(bbox: BoundingBox | str) -> str:
    return f"""
        [out:json];
        (
            (
                way[building]({bbox});
                way["building:part"]({bbox});
            );
            -
            (
                rel(bw:"outline");
                way(r:"outline");
            );
        );
        convert item ::=::,::geom=geom(),_osm_type=type();
        out geom;
    """


def query_building_with_hole(bbox: BoundingBox | str) -> str:
    return f"""
        [out:json];
           
                (
                    rel["building"]({bbox});
                   
                );
                
            (._;>;);
            out geom;

        """


def query_trees(bbox: BoundingBox | str) -> str:
    return f"""
         [out:json];
         node["natural"="tree"]({bbox});
         convert item ::=::,::geom=geom(),_osm_type=type();
         out geom;
     """


def query_tree_row(bbox: BoundingBox | str) -> str:
    return f"""
         [out:json];
         way["natural"="tree_row"]({bbox});
         convert item ::=::,::geom=geom(),_osm_type=type();
         out geom;
     """


def query_serviceroad(bbox: BoundingBox | str) -> str:
    return f"""
        [out:json];
            (
                
                way["highway"="service"]( {bbox});
                relation["highway"="service"]( {bbox});
            );
            (._;>;);
        out geom;
    """


def query_traffic_signals(bbox: BoundingBox | str) -> str:
    return f"""
         [out:json];
         node["crossing"="traffic_signals"]({bbox});
         convert item ::=::,::geom=geom(),_osm_type=type();
         out geom;
     """


def query_greenery(bbox: BoundingBox | str, tags: str) -> str:
    return f"""
        [out:json];
        way({bbox})->.all;
        (
            {tags}
        );
        convert item ::=::,::geom=geom(),_osm_type=type();
        out geom;
    """


def query_fountain(bbox: BoundingBox | str) -> str:
    return f"""
        [out:json];
        way["amenity"="fountain"]({bbox});
        (._;>;);
        out geom;
    """


def query_water(bbox: BoundingBox | str) -> str:
    return f"""
        [out:json];
        way["natural"="water"]({bbox});
        relation["natural"="water"]({bbox});
        (._;>;);
        out geom;
    """


def query_walk(bbox: BoundingBox | str) -> str:
    return f"""
        [out:json];
            (
                
                way["highway"="path"]( {bbox});
                way["highway"="footway"]( {bbox});
                way["highway"="pedestrian"]( {bbox});
                relation["highway"="path"]( {bbox});
                relation["highway"="footway"]( {bbox});
                relation["highway"="pedestrian"]( {bbox});
            );
            (._;>;);
        out geom;
    """


def query_tram_lines(bbox: BoundingBox | str) -> str:
    return f"""
         [out:json];
         relation["type"="route"]["route"="tram"]({bbox});
        
        convert item ::=::,::geom=geom(),_osm_type=type();
        out geom;
     """


def query_bike(bbox: BoundingBox | str) -> str:
    return f"""
         [out:json];
            way["bicycle"="designated"]({bbox});
            convert item ::=::,::geom=geom(),_osm_type=type();
            out geom;
     """
