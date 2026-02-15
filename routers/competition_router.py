from fastapi import APIRouter, Depends, HTTPException
from repositories.competition_repository import CompetitionRepository, get_competition_repository
from models.competition import Competition

router = APIRouter(
    prefix="/competitions",
    tags=["competitions"]
)

@router.post("/")
async def create_competition(
    competition: Competition, 
    competition_repository: CompetitionRepository = Depends(get_competition_repository)
):
    try:
        await competition_repository.insert_competition(competition)
        return {"message": "Competition created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def get_competitions(
    competition_repository: CompetitionRepository = Depends(get_competition_repository)
):
    try:
        return await competition_repository.get_competitions()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{name}")
async def get_competition_by_name(
    name: str, 
    competition_repository: CompetitionRepository = Depends(get_competition_repository)
):
    try:
        return await competition_repository.get_competition_by_name(name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))