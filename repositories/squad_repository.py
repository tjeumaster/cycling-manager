from fastapi import HTTPException
from db.database import db
from fastapi import Depends
from db.loader import queries
from models.squad import Squad
from models.cyclist import Cyclist
from dataclasses import dataclass
from asyncpg import Connection

@dataclass
class SquadRepository:
    conn: Connection | None = None

    async def create_squad(self, squad_name: str, user_id: int) -> Squad:
        row = await queries.create_squad(self.conn, name=squad_name, user_id=user_id)
        if not row:
            raise HTTPException(status_code=400, detail="Squad already exists")

        return Squad.model_validate(dict(row))

    async def get_squads_by_user(self, user_id: int) -> list[Squad]:
        try:
            rows = queries.get_squads_by_user(self.conn, user_id=user_id)
            return [Squad.model_validate(dict(row)) async for row in rows]

        except Exception as e:
            raise Exception(f"Failed to get squads: {str(e)}")

    async def get_squad_cyclists(self, squad_id: int) -> list[Cyclist]:
        try:
            rows = queries.get_squad_cyclists(self.conn, squad_id=squad_id)
            return [Cyclist.model_validate(dict(row)) async for row in rows]

        except Exception as e:
            raise Exception(f"Failed to get squad cyclists: {str(e)}")

    async def get_squad(self, squad_id: int) -> Squad:
        try:
            row = await queries.get_squad(self.conn, squad_id=squad_id)
            return Squad.model_validate(dict(row))
        except Exception as e:
            raise Exception(f"Failed to get squad: {str(e)}")

    async def remove_cyclists(self, squad_id: int):
        try:
            await queries.remove_cyclists(self.conn, squad_id=squad_id)
        except Exception as e:
            raise Exception(f"Failed to remove cyclists: {str(e)}")

    async def add_cyclist(self, squad_id: int, cyclist_id: int):
        try:
            await queries.add_cyclist(self.conn, squad_id=squad_id, cyclist_id=cyclist_id)
        except Exception as e:
            raise Exception(f"Failed to add cyclist: {str(e)}")

    async def remove_cyclist(self, squad_id: int, cyclist_id: int):
        try:
            await queries.remove_cyclist(self.conn, squad_id=squad_id, cyclist_id=cyclist_id)
        except Exception as e:
            raise Exception(f"Failed to remove cyclist: {str(e)}")

    async def get_squad_price(self, squad_ids: list[int]) -> int:
        try:
            return await queries.get_squad_price(self.conn, squad_ids=squad_ids)

        except Exception as e:
            raise Exception(f"Failed to get squad price: {str(e)}")

    async def delete_squad(self, squad_id: int) -> None:
        try:
            return await queries.delete_squad(self.conn, squad_id=squad_id)

        except Exception as e:
            raise Exception(f"Failed to delete squad: {str(e)}")

def get_squad_repository(
    conn: Connection = Depends(db.get_connection),
) -> SquadRepository:
    return SquadRepository(conn)
