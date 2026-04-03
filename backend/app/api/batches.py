from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.models.schemas import BatchCreate, BatchResponse, BatchScanRequest, UserRole
from app.core.database import sql1_db
from app.core.dependencies import get_current_user, require_role
from datetime import datetime
import uuid

router = APIRouter()


@router.post("/create", response_model=BatchResponse, status_code=status.HTTP_201_CREATED)
async def create_batch(
    batch_data: BatchCreate,
    current_user: dict = Depends(require_role([UserRole.ADMIN]))
):
    """Create a new dispatch batch (ADMIN only)"""
    try:
        batch_id = str(uuid.uuid4())
        
        # Create batch
        insert_data = {
            "id": batch_id,
            "transporter_id": batch_data.transporter_id,
            "destination": batch_data.destination,
            "status": "PENDING",
            "expected_delivery": batch_data.expected_delivery.isoformat()
        }
        
        batch_response = sql1_db.get_client().table("batches").insert(insert_data).execute()
        
        if not batch_response.data:
            raise HTTPException(status_code=500, detail="Failed to create batch")
        
        # Add assets to batch
        batch_assets = []
        for asset_id in batch_data.asset_ids:
            asset_data = {
                "batch_id": batch_id,
                "asset_id": asset_id,
                "scanned_at_dispatch": False,
                "scanned_at_delivery": False
            }
            sql1_db.get_client().table("batch_assets").insert(asset_data).execute()
            batch_assets.append(asset_data)
        
        # Log event
        await log_batch_event(batch_id, "BATCH_CREATED", current_user["user_id"])
        
        return BatchResponse(
            id=batch_id,
            transporter_id=batch_data.transporter_id,
            destination=batch_data.destination,
            status="PENDING",
            expected_delivery=batch_data.expected_delivery,
            created_at=datetime.utcnow(),
            assets=batch_assets
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[BatchResponse])
async def list_batches(current_user: dict = Depends(get_current_user)):
    """List all batches"""
    try:
        response = sql1_db.get_client().table("batches").select("*").order("created_at", desc=True).execute()
        
        batches = []
        for batch in response.data:
            # Get batch assets
            assets_response = sql1_db.get_client().table("batch_assets").select("*").eq("batch_id", batch["id"]).execute()
            
            batches.append(BatchResponse(
                id=batch["id"],
                transporter_id=batch["transporter_id"],
                destination=batch["destination"],
                status=batch["status"],
                expected_delivery=batch["expected_delivery"],
                created_at=batch["created_at"],
                assets=assets_response.data or []
            ))
        
        return batches
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{batch_id}", response_model=BatchResponse)
async def get_batch(batch_id: str, current_user: dict = Depends(get_current_user)):
    """Get batch details"""
    try:
        response = sql1_db.get_client().table("batches").select("*").eq("id", batch_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Batch not found")
        
        batch = response.data[0]
        
        assets_response = sql1_db.get_client().table("batch_assets").select("*").eq("batch_id", batch_id).execute()
        
        return BatchResponse(
            id=batch["id"],
            transporter_id=batch["transporter_id"],
            destination=batch["destination"],
            status=batch["status"],
            expected_delivery=batch["expected_delivery"],
            created_at=batch["created_at"],
            assets=assets_response.data or []
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{batch_id}/scan")
async def scan_asset_into_batch(
    batch_id: str,
    scan_data: BatchScanRequest,
    current_user: dict = Depends(require_role([UserRole.TRANSPORTER]))
):
    """Scan an asset into batch at dispatch"""
    try:
        # Check if asset belongs to batch
        asset_in_batch = sql1_db.get_client().table("batch_assets") \
            .select("*") \
            .eq("batch_id", batch_id) \
            .eq("asset_id", scan_data.asset_id) \
            .execute()
        
        if not asset_in_batch.data:
            raise HTTPException(status_code=400, detail="Asset not in batch")
        
        # Mark as scanned
        sql1_db.get_client().table("batch_assets") \
            .update({"scanned_at_dispatch": True}) \
            .eq("batch_id", batch_id) \
            .eq("asset_id", scan_data.asset_id) \
            .execute()
        
        return {"message": "Asset scanned successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{batch_id}/confirm")
async def confirm_batch_dispatch(
    batch_id: str,
    current_user: dict = Depends(require_role([UserRole.TRANSPORTER]))
):
    """Confirm all assets scanned and initiate dispatch"""
    try:
        # Check all assets scanned
        batch_assets = sql1_db.get_client().table("batch_assets") \
            .select("*") \
            .eq("batch_id", batch_id) \
            .execute()
        
        all_scanned = all(asset["scanned_at_dispatch"] for asset in batch_assets.data)
        
        if not all_scanned:
            raise HTTPException(status_code=400, detail="Not all assets have been scanned")
        
        # Update batch status to IN_TRANSIT
        sql1_db.get_client().table("batches") \
            .update({"status": "IN_TRANSIT"}) \
            .eq("id", batch_id) \
            .execute()
        
        # Update all assets status
        for asset in batch_assets.data:
            sql1_db.get_client().table("assets") \
                .update({"status": "IN_TRANSIT"}) \
                .eq("id", asset["asset_id"]) \
                .execute()
        
        await log_batch_event(batch_id, "DISPATCHED", current_user["user_id"])
        
        return {"message": "Batch dispatched successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def log_batch_event(batch_id: str, event_type: str, user_id: str):
    """Log batch event"""
    try:
        event_data = {
            "batch_id": batch_id,
            "user_id": user_id,
            "event_type": event_type,
            "created_at": datetime.utcnow().isoformat()
        }
        sql1_db.get_client().table("events").insert(event_data).execute()
    except Exception as e:
        print(f"Failed to log batch event: {str(e)}")
