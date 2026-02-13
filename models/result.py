from pydantic import BaseModel

class PcsResult(BaseModel):
    position: int | None = None
    cyclist_name: str
    team_name: str
    info: str | None = None
    
class RaceResultCreate(BaseModel):
    race_id: int
    cyclist_id: int | None = None
    position: int | None = None
    cyclist_full_name: str | None = None
    info: str | None = None
    
class RaceResult(BaseModel):
    id: int
    race_id: int
    cyclist_id: int | None = None
    position: int | None = None
    cyclist_full_name: str | None = None
    info: str | None = None
    