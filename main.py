from contextlib import asynccontextmanager
from fastapi import FastAPI
from db.database import db
from routers.sync_router import router as sync_router
from routers.base_router import router as base_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.connect()
    yield
    await db.disconnect()
    
app = FastAPI(lifespan=lifespan)
app.include_router(sync_router)
app.include_router(base_router)