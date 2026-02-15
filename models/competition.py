from pydantic import BaseModel

class Competition(BaseModel):
    id: int
    name: str
    created_by: int | None = None


class CompetitionRequest(BaseModel):
    name: str
    created_by: int | None = None