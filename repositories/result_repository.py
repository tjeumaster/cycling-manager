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
        
def get_result_repository(conn: Connection=Depends(db.get_connection)) -> ResultRepository:
    return ResultRepository(conn)