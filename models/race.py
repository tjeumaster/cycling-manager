from enum import StrEnum
from pydantic import BaseModel
from datetime import datetime   

class RaceCategory(StrEnum):
    WORLD_TOUR = "world-tour"
    MONUMENT = "monument"
    OTHER = "other"
    
class RaceStatus(StrEnum):
    PLANNED = "planned"
    FINISHED = "finished"
    CANCELED = "canceled"
    
class RaceCreate(BaseModel):
    name: str
    year: int
    start_timestamp: datetime
    category: RaceCategory
    status: RaceStatus = RaceStatus.PLANNED
    pcs_path: str | None = None

class Race(BaseModel):
    id: int
    name: str
    year: int
    start_timestamp: datetime
    category: RaceCategory
    status: RaceStatus
    pcs_path: str | None = None    
    
class RaceCategoryPointsCreate(BaseModel):
    category: RaceCategory
    position: int
    points: int
    
    
    