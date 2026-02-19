from asyncpg import Connection
from fastapi import Depends
from db.loader import queries
from dataclasses import dataclass
from db.database import db
from models.selection import SelectionCyclist

@dataclass
class SelectionRepository:
    conn: Connection | None = None

    async def get_squad_selection(self, squad_id: int) -> list[SelectionCyclist]:
        try:
            rows = queries.get_squad_selection(self.conn, squad_id=squad_id)
            if not rows:
                return []
            
            return [SelectionCyclist.model_validate(dict(row)) async for row in rows]
        except Exception as e:
            raise Exception(f"Failed to get squad selections: {str(e)}")
        
    async def insert_squad_selection(self, squad_id: int, cyclist_id: int, is_leader: bool) -> None:
        try:
            await queries.insert_squad_selection(self.conn, squad_id=squad_id, cyclist_id=cyclist_id, is_leader=is_leader)
        except Exception as e:
            raise Exception(f"Failed to insert squad selection: {str(e)}")
        
    async def delete_squad_selection_cyclist(self, squad_id: int, cyclist_id: int) -> None:
        try:
            await queries.delete_squad_selection_cyclist(self.conn, squad_id=squad_id, cyclist_id=cyclist_id)
        except Exception as e:
            raise Exception(f"Failed to delete squad selection cyclist: {str(e)}")
        
    async def delete_squad_selection(self, squad_id: int) -> None:
        try:
            await queries.delete_squad_selection(self.conn, squad_id=squad_id)
        
        except Exception as e:
            raise Exception(f"Failed to delete squad selection: {str(e)}")
    

def get_selection_repository(
    conn: Connection = Depends(db.get_connection)
) -> SelectionRepository:
    return SelectionRepository(conn)