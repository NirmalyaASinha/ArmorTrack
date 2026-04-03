from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models.schemas import GPSUpdateRequest, GPSResponse, UserRole
from app.core.database import sql1_db
from app.core.dependencies import require_role
from datetime import datetime
import math

router = APIRouter()


@router.post("/update")
async def update_gps(gps_data: GPSUpdateRequest, current_user: dict = Depends(require_role([UserRole.TRANSPORTER]))):
    """Update GPS location for a batch (called by ESP32)"""
    try:
        # Store GPS update
        gps_record = {
            "batch_id": gps_data.batch_id,
            "latitude": gps_data.latitude,
            "longitude": gps_data.longitude,
            "timestamp": gps_data.timestamp.isoformat()
        }
        
        sql1_db.get_client().table("gps_tracking").insert(gps_record).execute()
        
        # Check for alerts (geofence, stops, etc.)
        await check_gps_alerts(gps_data)
        
        return {"message": "GPS update received", "status": "OK"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/track/{batch_id}", response_model=List[GPSResponse])
async def get_batch_gps(batch_id: str, current_user: dict = Depends(require_role([UserRole.ADMIN, UserRole.WAREHOUSE]))):
    """Get GPS tracking history for a batch"""
    try:
        response = sql1_db.get_client().table("gps_tracking") \
            .select("*") \
            .eq("batch_id", batch_id) \
            .order("timestamp", desc=True) \
            .limit(100) \
            .execute()
        
        return [GPSResponse(
            batch_id=record["batch_id"],
            latitude=record["latitude"],
            longitude=record["longitude"],
            timestamp=record["timestamp"]
        ) for record in response.data]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/active")
async def get_active_batches_gps(current_user: dict = Depends(require_role([UserRole.ADMIN]))):
    """Get latest GPS position for all active batches"""
    try:
        # Get IN_TRANSIT batches
        batches = sql1_db.get_client().table("batches") \
            .select("id, destination") \
            .eq("status", "IN_TRANSIT") \
            .execute()
        
        active_batches = []
        for batch in batches.data:
            # Get latest GPS position
            gps_response = sql1_db.get_client().table("gps_tracking") \
                .select("*") \
                .eq("batch_id", batch["id"]) \
                .order("timestamp", desc=True) \
                .limit(1) \
                .execute()
            
            if gps_response.data:
                gps = gps_response.data[0]
                active_batches.append({
                    "batch_id": batch["id"],
                    "latitude": gps["latitude"],
                    "longitude": gps["longitude"],
                    "destination": batch["destination"],
                    "timestamp": gps["timestamp"]
                })
        
        return {"batches": active_batches}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def check_gps_alerts(gps_data: GPSUpdateRequest):
    """Check for geofence violations and other GPS alerts"""
    try:
        from app.core.config import settings
        
        # Get batch info
        batch = sql1_db.get_client().table("batches") \
            .select("*") \
            .eq("id", gps_data.batch_id) \
            .execute()
        
        if not batch.data:
            return
        
        batch_info = batch.data[0]
        
        # Get previous GPS position
        prev_gps = sql1_db.get_client().table("gps_tracking") \
            .select("*") \
            .eq("batch_id", gps_data.batch_id) \
            .order("timestamp", desc=True) \
            .limit(2) \
            .execute()
        
        if len(prev_gps.data) >= 2:
            prev = prev_gps.data[1]
            
            # Calculate distance from previous position
            distance = haversine_distance(
                prev["latitude"], prev["longitude"],
                gps_data.latitude, gps_data.longitude
            )
            
            # Check for unscheduled stop (less than 10m movement in 10 minutes)
            time_diff = (gps_data.timestamp - datetime.fromisoformat(prev["timestamp"])).total_seconds() / 60
            
            if distance < 0.01 and time_diff > settings.MAX_STOP_DURATION_MINUTES:
                # Create alert
                alert = {
                    "type": "UNSCHEDULED_STOP",
                    "severity": "WARNING",
                    "message": f"Batch {gps_data.batch_id} has stopped for over {settings.MAX_STOP_DURATION_MINUTES} minutes",
                    "batch_id": gps_data.batch_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
                sql1_db.get_client().table("alerts").insert(alert).execute()
        
        # TODO: Add geofence check against expected route
        
    except Exception as e:
        print(f"GPS alert check failed: {str(e)}")


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two GPS points in kilometers"""
    R = 6371  # Earth radius in km
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c
