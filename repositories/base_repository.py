from dataclasses import dataclass
from asyncpg import Connection
from fastapi import Depends
from db.loader import queries
from models.cyclist import Cyclist, CyclistCreate
from models.race import Race, RaceCategoryPointsCreate, RaceCreate
from models.team import Team, TeamCreate
from db.database import db
from config import settings

@dataclass
class BaseRepository:
    conn: Connection
    
    async def insert_team(self, team: TeamCreate):
        team_dict = team.model_dump()
        await queries.insert_team(self.conn, **team_dict)
    
    async def insert_cyclist(self, cyclist: CyclistCreate):
        cyclist_dict = cyclist.model_dump()
        await queries.insert_cyclist(self.conn, **cyclist_dict)
        
    async def get_teams(self) -> list[Team]:
        rows = queries.get_teams(self.conn)
        return [Team.model_validate(dict(row)) async for row in rows]
    
    async def get_cyclists(self) -> list[Cyclist]:
        rows = queries.get_cyclists(self.conn)
        return [Cyclist.model_validate(dict(row)) async for row in rows]
    
    async def insert_race(self, race: RaceCreate):
        race_dict = race.model_dump()
        await queries.insert_race(self.conn, **race_dict)
        
    async def get_races(self) -> list[Race]:
        rows = queries.get_races(self.conn)
        return [Race.model_validate(dict(row)) async for row in rows]
        
    async def insert_race_category_points(self, race_category_points: RaceCategoryPointsCreate):
        race_category_points_dict = race_category_points.model_dump()
        await queries.insert_race_category_points(self.conn, **race_category_points_dict)
        
    async def get_pcs_races(self) -> list[Race]:
        rows = queries.get_pcs_races(self.conn)
        return [Race.model_validate(dict(row)) async for row in rows]
    
    async def update_race_status(self, race_id: int, status: str):
        await queries.update_race_status(self.conn, id=race_id, status=status)

def get_base_repository(conn: Connection = Depends(db.get_connection)) -> BaseRepository:
    return BaseRepository(conn)