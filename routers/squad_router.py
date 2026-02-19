from loguru import logger
from config import settings
from models.user import User
from services.auth_service import get_current_user
from fastapi import HTTPException
from repositories.squad_repository import SquadRepository
from repositories.squad_repository import get_squad_repository
from fastapi import APIRouter, Depends


router = APIRouter(prefix="/squads", tags=["squads"])


@router.post(path="", summary="Create a new squad for user")
async def create_squad(
    squad_name: str, 
    squad_repository: SquadRepository = Depends(get_squad_repository),
    user: User = Depends(get_current_user)
):
    try:
        return await squad_repository.create_squad(squad_name, user.id)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get(path="", summary="Get all squads for current user")
async def get_squads(
    squad_repository: SquadRepository = Depends(get_squad_repository),
    user: User = Depends(get_current_user)
):
    try:
        return await squad_repository.get_squads_by_user(user.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get(path="/{id}/cyclists", summary="Get all cyclists for a squad")
async def get_squad_cyclists(
    id: int,
    race_id: int | None = None,
    squad_repository: SquadRepository = Depends(get_squad_repository),
    user: User = Depends(get_current_user)
):
    try:
        squad = await squad_repository.get_squad(id)
        if squad.user_id != user.id:
            raise HTTPException(status_code=403, detail="You do not have permission to view this squad")
        
        return await squad_repository.get_squad_cyclists(id, race_id=race_id)
    except Exception as e:  
        raise HTTPException(status_code=400, detail=str(e))

@router.post(path="/{id}/cyclists", summary="Add cyclists (list of cyclist ids) to a squad")
async def add_cyclists(
    id: int,
    cyclist_ids: list[int],
    squad_repository: SquadRepository = Depends(get_squad_repository),
    user: User = Depends(get_current_user)
):
    try:
        # check if squad belongs to user
        squad = await squad_repository.get_squad(id)
        if squad.user_id != user.id:
            raise HTTPException(status_code=403, detail="You do not have permission to modify this squad")
        # check length < max number of cyclists 
        if len(cyclist_ids) > settings.SQUAD_SIZE:
            raise HTTPException(status_code=400, detail="Squad size exceeds maximum limit")

        # Check if squad price is within budget
        squad_price = await squad_repository.get_squad_price(cyclist_ids)
        logger.info(f"Squad price: {squad_price}")
        if squad_price > settings.MAX_SQUAD_BUDGET:
            raise HTTPException(status_code=400, detail="Squad price exceeds budget")   

        # check if squad belongs to user
        squad = await squad_repository.get_squad(id)
        if squad.user_id != user.id:
            raise HTTPException(status_code=403, detail="You do not have permission to modify this squad")

        # delete previous squad cyclists
        await squad_repository.remove_cyclists(id)

        # add new squad cyclists
        for cyclist_id in cyclist_ids:
            await squad_repository.add_cyclist(id, cyclist_id)

        return {"message": "Squad updated successfully"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete(path="/{id}", summary="Delete a squad")
async def delete_squad(
    id: int,
    squad_repository: SquadRepository = Depends(get_squad_repository),
    user: User = Depends(get_current_user)
):
    try:
        squad = await squad_repository.get_squad(id)
        if squad.user_id != user.id:
            raise HTTPException(status_code=403, detail="You do not have permission to delete this squad")
        
        await squad_repository.delete_squad(id)
        
        return {"message": "Squad deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting squad: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
@router.delete(path="/{squad_id}/cyclists/{cyclist_id}", summary="Delete a cyclist from a squad")
async def delete_cyclist(
    squad_id: int,
    cyclist_id: int,
    squad_repository: SquadRepository = Depends(get_squad_repository),
    user: User = Depends(get_current_user)
):
    try:
        squad = await squad_repository.get_squad(squad_id)
        if squad.user_id != user.id:
            raise HTTPException(status_code=403, detail="You do not have permission to modify this squad")
        await squad_repository.remove_cyclist(squad_id, cyclist_id)
        return {"message": "Cyclist removed from squad successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
