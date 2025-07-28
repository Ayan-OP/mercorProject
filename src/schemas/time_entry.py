import uuid
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

# --- Main Time Entry Schemas (based on the 'Window' model) ---

class TimeWindowBase(BaseModel):
    """Base model for a time window, containing fields sent from the desktop app."""
    start: int # Timestamp in milliseconds
    end: int # Timestamp in milliseconds
    timezoneOffset: int
    
    projectId: str
    taskId: str
    taskStatus: Optional[str] = None
    taskPriority: Optional[str] = None
    
    note: Optional[str] = None
    
    # Computer/OS info
    computer: str
    user: str # OS username
    domain: Optional[str] = None
    os: str
    osVersion: str
    hwid: str # Hardware ID
    
class TimeWindowUpdate(BaseModel):
    """
    Schema for the admin request body to bulk-update time windows.
    All fields are optional.
    """
    taskStatus: Optional[str] = None
    taskPriority: Optional[str] = None
    paid: Optional[bool] = None
    billable: Optional[bool] = None
    note: Optional[str] = None
    billRate: Optional[float] = None
    overtimeBillRate: Optional[float] = None
    payRate: Optional[float] = None
    overtimePayRate: Optional[float] = None

class TimeWindowCreate(TimeWindowBase):
    """Schema for the request body when creating a new time window."""
    pass

class TimeWindowInDB(TimeWindowBase):
    """Represents a time window document as it is stored in MongoDB."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    employeeId: str # Added from the authenticated user's token
    shiftId: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organizationId: str = "default-org" # Placeholder
    
    # Using datetime internally for easier queries
    startTime: datetime
    endTime: datetime
    
    type: Literal["manual", "tracked"] = "tracked"
    billable: bool = True
    overtime: bool = False
    paid: bool = False
    
    # Financials
    billRate: Optional[float] = None
    overtimeBillRate: Optional[float] = None
    payRate: Optional[float] = None
    overtimePayRate: Optional[float] = None
    
    # Translated times (calculated on creation)
    startTranslated: int
    endTranslated: int

    class Config:
        populate_by_name = True

class TimeWindowResponse(BaseModel):
    """Schema for the response model returned by the API."""
    id: str
    employeeId: str
    shiftId: str
    organizationId: str
    
    start: int
    end: int
    timezoneOffset: int
    
    projectId: str
    taskId: str
    taskStatus: Optional[str] = None
    taskPriority: Optional[str] = None
    
    note: Optional[str] = None
    
    computer: str
    user: str
    domain: Optional[str] = None
    os: str
    osVersion: str
    hwid: str
    
    type: Literal["manual", "tracked"]
    billable: bool
    overtime: bool
    paid: bool
    
    billRate: Optional[float] = None
    overtimeBillRate: Optional[float] = None
    payRate: Optional[float] = None
    overtimePayRate: Optional[float] = None
    
    startTranslated: int
    endTranslated: int
