from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.models.schemas import AssetCreate, AssetResponse, AssetUpdate, UserRole
from app.core.database import sql1_db
from app.core.dependencies import get_current_user, require_role
from datetime import datetime

router = APIRouter()


@router.post("/register", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
async def register_asset(
    asset_data: AssetCreate,
    current_user: dict = Depends(require_role([UserRole.MANUFACTURER, UserRole.ADMIN]))
):
    """Register a new asset (MANUFACTURER or ADMIN only)"""
    try:
        # Generate unique asset ID
        import uuid
        asset_id = str(uuid.uuid4())
        
        # Insert asset into SQL_1
        insert_data = {
            "id": asset_id,
            "asset_name": asset_data.asset_name,
            "asset_type": asset_data.asset_type,
            "encrypted_payload": None,  # Will be encrypted in production
            "status": "WAREHOUSE",
            "current_custodian": None,
            "last_serviced_at": None,
            "service_interval_days": 90
        }
        
        response = sql1_db.get_client().table("assets").insert(insert_data).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to register asset"
            )
        
        asset = response.data[0]
        
        # Log event
        await log_asset_event(asset_id, "REGISTERED", current_user["user_id"])
        
        return AssetResponse(
            id=asset["id"],
            asset_name=asset["asset_name"],
            asset_type=asset["asset_type"],
            status=asset["status"],
            current_custodian=asset.get("current_custodian"),
            last_serviced_at=asset.get("last_serviced_at"),
            service_interval_days=asset["service_interval_days"],
            created_at=asset["created_at"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Asset registration failed: {str(e)}"
        )


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get asset details by ID"""
    try:
        response = sql1_db.get_client().table("assets").select("*").eq("id", asset_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found"
            )
        
        asset = response.data[0]
        
        return AssetResponse(
            id=asset["id"],
            asset_name=asset["asset_name"],
            asset_type=asset["asset_type"],
            status=asset["status"],
            current_custodian=asset.get("current_custodian"),
            last_serviced_at=asset.get("last_serviced_at"),
            service_interval_days=asset["service_interval_days"],
            created_at=asset["created_at"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve asset: {str(e)}"
        )


@router.get("/", response_model=List[AssetResponse])
async def list_assets(
    current_user: dict = Depends(require_role([UserRole.ADMIN, UserRole.WAREHOUSE]))
):
    """List all assets (ADMIN or WAREHOUSE only)"""
    try:
        response = sql1_db.get_client().table("assets").select("*").order("created_at", desc=True).execute()
        
        assets = []
        for asset in response.data:
            assets.append(AssetResponse(
                id=asset["id"],
                asset_name=asset["asset_name"],
                asset_type=asset["asset_type"],
                status=asset["status"],
                current_custodian=asset.get("current_custodian"),
                last_serviced_at=asset.get("last_serviced_at"),
                service_interval_days=asset["service_interval_days"],
                created_at=asset["created_at"]
            ))
        
        return assets
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve assets: {str(e)}"
        )


@router.put("/{asset_id}", response_model=AssetResponse)
async def update_asset(
    asset_id: str,
    asset_update: AssetUpdate,
    current_user: dict = Depends(require_role([UserRole.ADMIN, UserRole.WAREHOUSE]))
):
    """Update asset information"""
    try:
        # Build update data
        update_data = asset_update.model_dump(exclude_unset=True)
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No update data provided"
            )
        
        response = sql1_db.get_client().table("assets").update(update_data).eq("id", asset_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found"
            )
        
        asset = response.data[0]
        
        return AssetResponse(
            id=asset["id"],
            asset_name=asset["asset_name"],
            asset_type=asset["asset_type"],
            status=asset["status"],
            current_custodian=asset.get("current_custodian"),
            last_serviced_at=asset.get("last_serviced_at"),
            service_interval_days=asset["service_interval_days"],
            created_at=asset["created_at"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update asset: {str(e)}"
        )


async def log_asset_event(asset_id: str, event_type: str, user_id: str, metadata: dict = None):
    """Log an asset event (internal helper)"""
    try:
        event_data = {
            "asset_id": asset_id,
            "user_id": user_id,
            "event_type": event_type,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat()
        }
        
        sql1_db.get_client().table("events").insert(event_data).execute()
    except Exception as e:
        print(f"Failed to log event: {str(e)}")
