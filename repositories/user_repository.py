from asyncpg import Connection
from dataclasses import dataclass
from db.database import db
from db.loader import queries
from fastapi import Depends
from models.user import User, UserCreate


@dataclass
class UserRepository:
    conn: Connection | None = None

    async def insert_user(self, user: UserCreate, password_hash: str) -> int:
        return await queries.insert_user(
            self.conn,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            password_hash=password_hash,
        )

    async def get_user_by_email(self, email: str) -> User | None:
        row = await queries.get_user_by_email(self.conn, email=email)
        if row:
            return User.model_validate(dict(row))
        return None


def get_user_repository(
    conn: Connection = Depends(db.get_connection),
) -> UserRepository:
    return UserRepository(conn)
