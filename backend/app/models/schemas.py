from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum


# Enums
class UserRole(str, Enum):
    MANUFACTURER = "MANUFACTURER"
    TRANSPORTER = "TRANSPORTER"
    WAREHOUSE = "WAREHOUSE"
    ADMIN = "ADMIN"
    AUDITOR = "AUDITOR"


class AssetStatus(str, Enum):
    WAREHOUSE = "WAREHOUSE"
    IN_TRANSIT = "IN_TRANSIT"
    DEPLOYED = "DEPLOYED"
    MAINTENANCE = "MAINTENANCE"
    CHECKED_OUT = "CHECKED_OUT"


class BatchStatus(str, Enum):
    PENDING = "PENDING"
    IN_TRANSIT = "IN_TRANSIT"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class EventType(str, Enum):
    REGISTERED = "REGISTERED"
    DISPATCHED = "DISPATCHED"
    IN_TRANSIT = "IN_TRANSIT"
    DELIVERED = "DELIVERED"
    CHECKED_OUT = "CHECKED_OUT"
    RETURNED = "RETURNED"
    MAINTAINED = "MAINTAINED"
    CUSTODY_TRANSFER = "CUSTODY_TRANSFER"


class AlertSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ALERT = "ALERT"
    CRITICAL = "CRITICAL"


# Auth Models
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    role: UserRole


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole
    rfid_tag: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: UserRole
    rfid_tag: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Asset Models
class AssetCreate(BaseModel):
    asset_name: str
    asset_type: str
    metadata: Optional[dict] = None


class AssetResponse(BaseModel):
    id: str
    asset_name: str
    asset_type: str
    status: AssetStatus
    current_custodian: Optional[str] = None
    last_serviced_at: Optional[datetime] = None
    service_interval_days: int = 90
    created_at: datetime
    
    class Config:
        from_attributes = True


class AssetUpdate(BaseModel):
    asset_name: Optional[str] = None
    asset_type: Optional[str] = None
    status: Optional[AssetStatus] = None
    current_custodian: Optional[str] = None


# Batch Models
class BatchCreate(BaseModel):
    transporter_id: str
    destination: str
    asset_ids: List[str]
    expected_delivery: datetime


class BatchResponse(BaseModel):
    id: str
    transporter_id: str
    destination: str
    status: BatchStatus
    expected_delivery: datetime
    created_at: datetime
    assets: List[dict] = []
    
    class Config:
        from_attributes = True


class BatchScanRequest(BaseModel):
    asset_id: str


# GPS Models
class GPSUpdateRequest(BaseModel):
    batch_id: str
    latitude: float
    longitude: float
    timestamp: datetime


class GPSResponse(BaseModel):
    batch_id: str
    latitude: float
    longitude: float
    timestamp: datetime


# Armoury Models
class CheckoutRequest(BaseModel):
    asset_id: str
    personnel_id: str


class ReturnRequest(BaseModel):
    asset_id: str
    personnel_id: str


# Audit Models
class AuditLogResponse(BaseModel):
    id: int
    event_id: str
    event_data: dict
    entry_hash: str
    prev_hash: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class AuditVerifyResponse(BaseModel):
    status: str  # "OK" or "TAMPERED"
    total_entries: int
    tampered_entries: List[int] = []
    message: str


# Maintenance Models
class MaintenanceCompleteRequest(BaseModel):
    asset_id: str
    technician_id: str
    notes: Optional[str] = None


class MaintenanceDueResponse(BaseModel):
    id: str
    asset_name: str
    asset_type: str
    last_serviced_at: Optional[datetime]
    service_interval_days: int
    days_until_due: int
    status: str  # "OVERDUE", "DUE_SOON", "OK"


# Alert Models
class AlertResponse(BaseModel):
    id: str
    type: str
    severity: AlertSeverity
    message: str
    batch_id: Optional[str] = None
    asset_id: Optional[str] = None
    timestamp: datetime
    dismissed: bool = False
    
    class Config:
        from_attributes = True


# Health Check
class HealthResponse(BaseModel):
    backend: bool
    sql1: bool
    sql2: bool
    timestamp: datetime
