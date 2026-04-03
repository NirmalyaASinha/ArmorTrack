from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models.schemas import AlertResponse, UserRole
from app.core.database import sql1_db
from app.core.dependencies import require_role

router = APIRouter()


@router.get("/active")
async def get_active_alerts(current_user: dict = Depends(require_role([UserRole.ADMIN, UserRole.WAREHOUSE]))):
    """Get all active (non-dismissed) alerts"""
    try:
        response = sql1_db.get_client().table("alerts") \
            .select("*") \
            .eq("dismissed", False) \
            .order("timestamp", desc=True) \
            .limit(50) \
            .execute()
        
        alerts = []
        for alert in response.data:
            alerts.append(AlertResponse(
                id=alert["id"],
                type=alert["type"],
                severity=alert["severity"],
                message=alert["message"],
                batch_id=alert.get("batch_id"),
                asset_id=alert.get("asset_id"),
                timestamp=alert["timestamp"],
                dismissed=alert.get("dismissed", False)
            ))
        
        return {"alerts": alerts, "total": len(alerts)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{alert_id}/dismiss")
async def dismiss_alert(
    alert_id: str,
    current_user: dict = Depends(require_role([UserRole.ADMIN, UserRole.WAREHOUSE]))
):
    """Dismiss an alert"""
    try:
        sql1_db.get_client().table("alerts") \
            .update({"dismissed": True}) \
            .eq("id", alert_id) \
            .execute()
        
        return {"message": "Alert dismissed successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
