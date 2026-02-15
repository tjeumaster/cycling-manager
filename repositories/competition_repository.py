from dataclasses import dataclass
from models.competition import Competition
from db.loader import queries
from asyncpg import Connection
from fastapi import Depends
from db.database import db

@dataclass
class CompetitionRepository:
    conn: Connection | None = None

    async def insert_competition(self, competition: Competition):
        await queries.insert_competition(
            self.conn, 
            name=competition.name, 
            created_by=competition.created_by
        )

    async def get_competitions(self):
        rows = await queries.get_competitions(self.conn)
        return [Competition.model_validate(row) for row in rows]

    async def get_competition_by_name(self, name: str):
        row = await queries.get_competition_by_name(self.conn, name=name)
        return Competition.model_validate(row)

def get_competition_repository(
    conn: Connection=Depends(db.get_connection)
) -> CompetitionRepository:
    return CompetitionRepository(conn)


        