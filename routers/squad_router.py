from loguru import logger
from config import settings
from models.user import User
from services.auth_service import get_current_user
from fastapi import HTTPException
from repositories.squad_repository import SquadRepository
from repositories.squad_repository import get_squad_repository
from fastapi import APIRouter, Depends


router = APIRouter(prefix="/squads", tags=["squads"])


@router.post(path="", description="Create a new squad")
async def create_squad(
    squad_name: str, 
    squad_repository: SquadRepository = Depends(get_squad_repository),
    user: User = Depends(get_current_user)
):
    try:
        return await squad_repository.create_squad(squad_name, user.id)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get(path="", description="Get all squads for current user")
async def get_squads(
    squad_repository: SquadRepository = Depends(get_squad_repository),
    user: User = Depends(get_current_user)
):
    try:
        return await squad_repository.get_squads_by_user(user.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get(path="/cyclists", description="Get all cyclists for a squad")
async def get_squad_cyclists(
    squad_id: int,
    squad_repository: SquadRepository = Depends(get_squad_repository),
    user: User = Depends(get_current_user)
):
    try:
        return await squad_repository.get_squad_cyclists(squad_id, user.id)
    except Exception as e:  
        raise HTTPException(status_code=400, detail=str(e))

@router.post(path="/cyclists", description="Add cyclists to a squad")
async def add_cyclists(
    squad_id: int,
    cyclist_ids: list[int],
    squad_repository: SquadRepository = Depends(get_squad_repository),
    user: User = Depends(get_current_user)
):
    try:
        # check length < max number of cyclists 
        if len(cyclist_ids) > settings.SQUAD_SIZE:
            raise HTTPException(status_code=400, detail="Squad size exceeds maximum limit")

        # Check if squad price is within budget
        squad_price = await squad_repository.get_squad_price(cyclist_ids)
        logger.info(f"Squad price: {squad_price}")
        if squad_price > settings.MAX_SQUAD_BUDGET:
            raise HTTPException(status_code=400, detail="Squad price exceeds budget")   

        # check if squad belongs to user
        squad = await squad_repository.get_squad(squad_id)
        if squad.user_id != user.id:
            raise HTTPException(status_code=403, detail="You do not have permission to modify this squad")

        # delete previous squad cyclists
        await squad_repository.remove_cyclists(squad_id)

        # add new squad cyclists
        for cyclist_id in cyclist_ids:
            await squad_repository.add_cyclist(squad_id, cyclist_id)

        return {"message": "Squad updated successfully"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

