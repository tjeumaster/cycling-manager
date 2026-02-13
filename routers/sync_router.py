from fastapi import APIRouter, Depends, HTTPException

from services.sync_service import SyncService, get_sync_service

router = APIRouter(prefix="/sync", tags=["sync"])

@router.post("")
async def sync_data(sync_service: SyncService = Depends(get_sync_service)):
    try:
        await sync_service.sync()
        return {"message": "Data synchronization completed successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/race-results")
async def sync_race_results(
    sync_service: SyncService = Depends(get_sync_service)
):
    try:
        await sync_service.sync_race_results()
        return {"message": f"Race results synchronized successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/pcs-races")
async def sync_pcs_races(
    year: int,
    sync_service: SyncService = Depends(get_sync_service)
):
    try:
        await sync_service.sync_pcs_races(year)
        return {"message": f"Races for year {year} synchronized successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 