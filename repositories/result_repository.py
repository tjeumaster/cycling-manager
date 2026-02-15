from models.result import RaceResult
from dataclasses import dataclass
from asyncpg import Connection
from fastapi import Depends
from models.result import RaceResultCreate
from db.loader import queries
from db.database import db

@dataclass
class ResultRepository:
    conn: Connection
    
    async def insert_race_result(self, race_result: RaceResultCreate):
        race_result_dict = race_result.model_dump()
        await queries.insert_race_result(self.conn, **race_result_dict)

    async def get_race_results(self, race_id: int) -> list[RaceResult]:
        rows = queries.get_race_results(self.conn, race_id=race_id)
        return [RaceResult.model_validate(dict(row)) async for row in rows]
        
def get_result_repository(conn: Connection=Depends(db.get_connection)) -> ResultRepository:
    return ResultRepository(conn)