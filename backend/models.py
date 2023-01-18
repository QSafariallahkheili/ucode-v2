from dataclasses import dataclass

from pydantic import BaseModel


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