from pydantic import BaseModel

class TeamCreate(BaseModel):
    code: str
    name: str
    image_url: str

class Team(BaseModel):
    id: int
    code: str
    name: str
    image_url: str
