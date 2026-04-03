from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models.schemas import MaintenanceDueResponse, MaintenanceCompleteRequest, UserRole
from app.core.database import sql1_db
from app.core.dependencies import require_role
from datetime import datetime, timedelta

router = APIRouter()


@router.get("/due")
async def get_maintenance_due(
    current_user: dict = Depends(require_role([UserRole.ADMIN]))
):
    """Get assets due for maintenance"""
    try:
        from app.core.config import settings
        
        # Get all assets
        assets = sql1_db.get_client().table("assets") \
            .select("*") \
            .execute()
        
        due_assets = []
        now = datetime.utcnow()
        
        for asset in assets.data:
            last_serviced = asset.get("last_serviced_at")
            interval_days = asset.get("service_interval_days", 90)
            
            if last_serviced:
                last_serviced_dt = datetime.fromisoformat(last_serviced.replace('Z', '+00:00'))
                next_service = last_serviced_dt + timedelta(days=interval_days)
                days_until_due = (next_service - now).days
            else:
                # Never serviced
                days_until_due = 0
            
            # Determine status
            if days_until_due < 0:
                status = "OVERDUE"
            elif days_until_due <= settings.MAINTENANCE_WARNING_DAYS:
                status = "DUE_SOON"
            else:
                continue  # Not due yet
            
            due_assets.append(MaintenanceDueResponse(
                id=asset["id"],
                asset_name=asset["asset_name"],
                asset_type=asset["asset_type"],
                last_serviced_at=asset.get("last_serviced_at"),
                service_interval_days=interval_days,
                days_until_due=days_until_due,
                status=status
            ))
        
        # Sort by urgency
        due_assets.sort(key=lambda x: x.days_until_due)
        
        return {"assets": due_assets, "total": len(due_assets)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/complete")
async def mark_maintenance_complete(
    request: MaintenanceCompleteRequest,
    current_user: dict = Depends(require_role([UserRole.ADMIN]))
):
    """Mark asset maintenance as complete"""
    try:
        # Update asset
        sql1_db.get_client().table("assets") \
            .update({
                "last_serviced_at": datetime.utcnow().isoformat(),
                "status": "WAREHOUSE"
            }) \
            .eq("id", request.asset_id) \
            .execute()
        
        # Log maintenance event
        event_data = {
            "asset_id": request.asset_id,
            "user_id": request.technician_id,
            "event_type": "MAINTAINED",
            "metadata": {"notes": request.notes},
            "created_at": datetime.utcnow().isoformat()
        }
        sql1_db.get_client().table("events").insert(event_data).execute()
        
        return {"message": "Maintenance completed successfully", "asset_id": request.asset_id}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schedule")
async def get_maintenance_schedule(
    current_user: dict = Depends(require_role([UserRole.ADMIN]))
):
    """Get full maintenance schedule for all assets"""
    try:
        assets = sql1_db.get_client().table("assets").select("*").execute()
        
        schedule = []
        now = datetime.utcnow()
        
        for asset in assets.data:
            last_serviced = asset.get("last_serviced_at")
            interval_days = asset.get("service_interval_days", 90)
            
            if last_serviced:
                last_serviced_dt = datetime.fromisoformat(last_serviced.replace('Z', '+00:00'))
                next_service = last_serviced_dt + timedelta(days=interval_days)
                days_until_due = (next_service - now).days
            else:
                days_until_due = -999  # Never serviced
            
            schedule.append({
                "id": asset["id"],
                "asset_name": asset["asset_name"],
                "asset_type": asset["asset_type"],
                "last_serviced_at": last_serviced,
                "next_service_date": (datetime.utcnow() + timedelta(days=days_until_due)).isoformat() if days_until_due > -999 else None,
                "service_interval_days": interval_days,
                "days_until_due": days_until_due
            })
        
        # Sort by next service date
        schedule.sort(key=lambda x: x["days_until_due"])
        
        return {"schedule": schedule, "total": len(schedule)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
