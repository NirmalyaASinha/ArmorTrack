from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import CheckoutRequest, ReturnRequest, UserRole
from app.core.database import sql1_db
from app.core.dependencies import require_role
from datetime import datetime

router = APIRouter()


@router.post("/checkout")
async def checkout_asset(
    request: CheckoutRequest,
    current_user: dict = Depends(require_role([UserRole.WAREHOUSE]))
):
    """Checkout asset from armoury (RFID gate)"""
    try:
        # Verify asset exists and is in warehouse
        asset = sql1_db.get_client().table("assets") \
            .select("*") \
            .eq("id", request.asset_id) \
            .execute()
        
        if not asset.data:
            raise HTTPException(status_code=404, detail="Asset not found")
        
        if asset.data[0]["status"] != "WAREHOUSE":
            raise HTTPException(status_code=400, detail="Asset is not available for checkout")
        
        # Update asset status
        sql1_db.get_client().table("assets") \
            .update({
                "status": "CHECKED_OUT",
                "current_custodian": request.personnel_id
            }) \
            .eq("id", request.asset_id) \
            .execute()
        
        # Log custody transfer
        event_data = {
            "asset_id": request.asset_id,
            "user_id": request.personnel_id,
            "event_type": "CHECKED_OUT",
            "metadata": {"previous_status": "WAREHOUSE"},
            "created_at": datetime.utcnow().isoformat()
        }
        sql1_db.get_client().table("events").insert(event_data).execute()
        
        return {"message": "Asset checked out successfully", "asset_id": request.asset_id}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/return")
async def return_asset(
    request: ReturnRequest,
    current_user: dict = Depends(require_role([UserRole.WAREHOUSE]))
):
    """Return asset to armoury (RFID gate)"""
    try:
        # Verify asset exists and is checked out
        asset = sql1_db.get_client().table("assets") \
            .select("*") \
            .eq("id", request.asset_id) \
            .execute()
        
        if not asset.data:
            raise HTTPException(status_code=404, detail="Asset not found")
        
        if asset.data[0]["status"] != "CHECKED_OUT":
            raise HTTPException(status_code=400, detail="Asset is not checked out")
        
        # Update asset status
        sql1_db.get_client().table("assets") \
            .update({
                "status": "WAREHOUSE",
                "current_custodian": None
            }) \
            .eq("id", request.asset_id) \
            .execute()
        
        # Log custody transfer
        event_data = {
            "asset_id": request.asset_id,
            "user_id": request.personnel_id,
            "event_type": "RETURNED",
            "metadata": {"previous_status": "CHECKED_OUT"},
            "created_at": datetime.utcnow().isoformat()
        }
        sql1_db.get_client().table("events").insert(event_data).execute()
        
        return {"message": "Asset returned successfully", "asset_id": request.asset_id}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/custody/{asset_id}")
async def get_custody_history(
    asset_id: str,
    current_user: dict = Depends(require_role([UserRole.ADMIN, UserRole.WAREHOUSE]))
):
    """Get custody history for an asset"""
    try:
        events = sql1_db.get_client().table("events") \
            .select("*") \
            .eq("asset_id", asset_id) \
            .in_("event_type", ["CHECKED_OUT", "RETURNED", "CUSTODY_TRANSFER"]) \
            .order("created_at", desc=True) \
            .execute()
        
        return {"asset_id": asset_id, "custody_events": events.data}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
