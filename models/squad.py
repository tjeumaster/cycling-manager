from pydantic import BaseModel

class SquadBase(BaseModel):
    name: str
    user_id: int

class Squad(BaseModel):
    id: int
    name: str
    user_id: int

class CreateSquadRequest(SquadBase):
    pass

