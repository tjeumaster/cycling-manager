from fastapi import APIRouter, Depends, HTTPException

from services.sync_service import SyncService, get_sync_service
from services.auth_service import get_current_user

router = APIRouter(prefix="/sync", tags=["sync"], dependencies=[Depends(get_current_user)])

@router.post("")
async def sync_data(sync_service: SyncService = Depends(get_sync_service)):
    try:
        await sync_service.sync()
        return {"message": "Data synchronization completed successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/races/results")
async def sync_race_results(
    year: int,
    sync_service: SyncService = Depends(get_sync_service)
):
    try:
        await sync_service.sync_race_results(year)
        return {"message": f"Race results for year {year} synchronized successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/races")
async def sync_pcs_races(
    year: int,
    sync_service: SyncService = Depends(get_sync_service)
):
    try:
        await sync_service.sync_pcs_races(year)
        return {"message": f"Races for year {year} synchronized successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 

@router.post("/races/startlist")
async def sync_pcs_startlist(
    year: int,
    sync_service: SyncService = Depends(get_sync_service)
):
    try:
        await sync_service.sync_startlist(year)
        return {"message": "PCS startlist synchronized successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
