from contextlib import asynccontextmanager
from fastapi import FastAPI
from db.database import db
from routers.sync_router import router as sync_router
from routers.base_router import router as base_router
from routers.competition_router import router as competition_router
from routers.auth_router import router as auth_router
from routers.squad_router import router as squad_router
from routers.selection_router import router as selection_router
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.connect()
    yield
    await db.disconnect()


app = FastAPI(lifespan=lifespan)
app.include_router(sync_router)
app.include_router(base_router)
app.include_router(competition_router)
app.include_router(auth_router)
app.include_router(squad_router)
app.include_router(selection_router)
#Add cors middleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)