from models.result import RaceResult
from fastapi import APIRouter, Depends, HTTPException
from models.cyclist import Cyclist
from models.race import Race
from repositories.base_repository import BaseRepository, get_base_repository

router = APIRouter()

@router.get("/cyclists")
async def get_cyclists(
    repository: BaseRepository = Depends(get_base_repository)
) -> list[Cyclist]:
    try:
        return await repository.get_cyclists()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/teams")
async def get_teams(
    repository: BaseRepository = Depends(get_base_repository)
):
    try:
        return await repository.get_teams()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/races")
async def get_races(
    repository: BaseRepository = Depends(get_base_repository)
) -> list[Race]:
    try:
        return await repository.get_races()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/races/cyclists")
async def get_race_cyclists(
    race_id: int,
    repository: BaseRepository = Depends(get_base_repository)
) -> list[Cyclist]:
    try:
        return await repository.get_race_cyclists(race_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/races/results")
async def get_race_results(
    race_id: int,
    repository: BaseRepository = Depends(get_base_repository)
) -> list[RaceResult]:
    try:
        return await repository.get_race_results(race_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    