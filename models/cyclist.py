from datetime import date
from pydantic import BaseModel, computed_field

class CyclistCreate(BaseModel):
    first_name: str
    last_name: str
    price: float
    birth_date: date
    nationality: str
    team_id: int
    image_url: str
    pcs_path: str | None = None

class Cyclist(BaseModel):
    id: int
    first_name: str
    last_name: str
    price: float
    birth_date: date
    nationality: str
    team_id: int
    team_name: str
    team_code: str
    team_image_url: str
    image_url: str
    is_participating: bool | None = None
    
    @computed_field
    @property
    def age(self) -> int:
        today = date.today()
        age = today.year - self.birth_date.year
        if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
            age -= 1
        return age
    
    @computed_field
    @property
    def full_name(self) -> str:
        return f"{self.last_name} {self.first_name}"
    