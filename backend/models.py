from dataclasses import astuple, dataclass

@dataclass
class BoundingBox:
    xmin: float
    ymin: float
    xmax: float
    ymax: float

    def __str__(self):
        return f"{self.ymin},{self.xmin},{self.ymax},{self.xmax}"


@dataclass
class ProjectSpecification:
    projectId: str
    bbox: BoundingBox


@dataclass
class LatLngPosition:
    lng: float
    lat: float
@dataclass
class MapOrientation:
    center: LatLngPosition
    zoom: float
    bearing: float
    pitch: float
@dataclass
class UpdateStartingOrientation:
    projectId: str
    startingOrientation: MapOrientation