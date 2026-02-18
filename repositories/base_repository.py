from config import settings
from dataclasses import dataclass
from datetime import datetime, timezone
from asyncpg import Connection
from fastapi import Depends
from db.loader import queries
from models.cyclist import Cyclist, CyclistCreate
from models.race import Race, RaceCategoryPointsCreate, RaceCreate
from models.team import Team, TeamCreate
from db.database import db

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
        year = settings.YEAR
        rows = queries.get_races(self.conn, year=year)
        races: list[Race] = []
        async for row in rows:
            data = dict(row)
            ts = data.get("start_timestamp")
            if ts is not None:
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=timezone.utc)
                data["start_timestamp"] = ts.astimezone()
            races.append(Race.model_validate(data))

        return races
        
    async def insert_race_category_points(self, race_category_points: RaceCategoryPointsCreate):
        race_category_points_dict = race_category_points.model_dump()
        await queries.insert_race_category_points(self.conn, **race_category_points_dict)
        
    async def get_pcs_races(self, year: int) -> list[Race]:
        rows = queries.get_pcs_races(self.conn, year=year)
        races: list[Race] = []
        async for row in rows:
            data = dict(row)
            ts = data.get("start_timestamp")
            if ts is not None:
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=timezone.utc)
                data["start_timestamp"] = ts.astimezone()
            races.append(Race.model_validate(data))

        return races
    
    async def update_race_status(self, race_id: int, status: str):
        await queries.update_race_status(self.conn, id=race_id, status=status)

    async def insert_race_cyclist(self, race_id: int, cyclist_id: int):
        await queries.insert_race_cyclist(self.conn, race_id=race_id, cyclist_id=cyclist_id)

    async def get_race_cyclists(self, race_id: int) -> list[Cyclist]:
        rows = queries.get_race_cyclists(self.conn, race_id=race_id)
        return [Cyclist.model_validate(dict(row)) async for row in rows]

    async def delete_race_cyclists(self, race_id: int):
        await queries.delete_race_cyclists(self.conn, race_id=race_id)

    async def get_next_race(self) -> Race:
        row = await queries.get_next_race(self.conn)
        data = dict(row)
        ts = data.get("start_timestamp")
        if ts is not None:
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            data["start_timestamp"] = ts.astimezone()

        return Race.model_validate(data)   


def get_base_repository(conn: Connection = Depends(db.get_connection)) -> BaseRepository:
    return BaseRepository(conn)