from pydantic import BaseModel
from models.cyclist import Cyclist

class CreateSquadSelection(BaseModel):
    cyclist_id: int
    squad_id: int
    is_leader: bool
    
class SelectionCyclist(Cyclist):
    is_leader: bool