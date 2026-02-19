from fastapi import APIRouter, Depends, HTTPException
from models.cyclist import Cyclist
from models.selection import CreateSquadSelection, SelectionCyclist
from repositories.selection_repository import SelectionRepository, get_selection_repository
from repositories.squad_repository import SquadRepository, get_squad_repository
from services.auth_service import get_current_user
from config import settings
from loguru import logger

router = APIRouter(
    prefix="/selections",
    tags=["selections"]
)

@router.get("/{squad_id}")
async def get_squad_selection(
    squad_id: int,
    selection_repository: SelectionRepository = Depends(get_selection_repository)
) -> list[SelectionCyclist]:
    try:
        return await selection_repository.get_squad_selection(squad_id=squad_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/{squad_id}")
async def insert_squad_selection(
    squad_id: int,
    squad_selection: list[CreateSquadSelection],
    selection_repository: SelectionRepository = Depends(get_selection_repository),
    squad_repository: SquadRepository = Depends(get_squad_repository),
    user = Depends(get_current_user)
):
    try:
        # Check if squad_id belongs to the user
        squad = await squad_repository.get_squad(squad_id)
        if squad.user_id != user.id:
            raise HTTPException(status_code=403, detail="You do not have permission to modify this squad")
        
        # Check if squad selection contains 12 cyclists and exactly 1 leader
        if len(squad_selection) != settings.SELECTION_SIZE:
            raise HTTPException(status_code=400, detail=f"Squad selection must contain exactly {settings.SELECTION_SIZE} cyclists")
        
        if sum(selection.is_leader for selection in squad_selection) != 1:
            raise HTTPException(status_code=400, detail="Squad selection must contain exactly 1 leader")
           
        # First delete existing selections for the squad
        await selection_repository.delete_squad_selection(squad_id=squad_id)
        
        # Get all cyclists of squad to check if the selected cyclists belong to the squad
        squad_cyclists = await squad_repository.get_squad_cyclists(squad_id=squad_id)
        squad_cyclist_ids = {cyclist.id for cyclist in squad_cyclists}
        for selection in squad_selection:
            if selection.cyclist_id not in squad_cyclist_ids:
                raise HTTPException(status_code=400, detail=f"Cyclist with id {selection.cyclist_id} does not belong to the squad")
        
        # Then insert new selections
        for selection in squad_selection:          
            await selection_repository.insert_squad_selection(
                squad_id=squad_id,
                cyclist_id=selection.cyclist_id,
                is_leader=selection.is_leader
            )
        return {"message": "Squad selection inserted successfully"}
    
    except Exception as e:
        logger.error(f"Error inserting squad selection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete("/{squad_id}/cyclists/{cyclist_id}")
async def delete_squad_selection_cyclist(
    squad_id: int,
    cyclist_id: int,
    selection_repository: SelectionRepository = Depends(get_selection_repository),
    squad_repository: SquadRepository = Depends(get_squad_repository),
    user = Depends(get_current_user)
):
    try:
        # Check if squad_id belongs to the user
        squad = await squad_repository.get_squad(squad_id)
        if squad.user_id != user.id:
            raise HTTPException(status_code=403, detail="You do not have permission to modify this squad")
        
        await selection_repository.delete_squad_selection_cyclist(squad_id=squad_id, cyclist_id=cyclist_id)
        return {"message": "Cyclist deleted from squad selection successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete("/{squad_id}")
async def delete_squad_selection(
    squad_id: int,
    selection_repository: SelectionRepository = Depends(get_selection_repository),
    squad_repository: SquadRepository = Depends(get_squad_repository),
    user = Depends(get_current_user)
):
    try:
        # Check if squad_id belongs to the user
        squad = await squad_repository.get_squad(squad_id)
        if squad.user_id != user.id:
            raise HTTPException(status_code=403, detail="You do not have permission to modify this squad")
        
        await selection_repository.delete_squad_selection(squad_id=squad_id)
        return {"message": "Squad selection deleted successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))