from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Literal
from datetime import datetime
import uuid



class SystemPermissions(BaseModel):
    """Corresponds to ISystemPermissions in the API documentation."""
    accessibility: Literal["authorized", "denied", "undetermined"] = "undetermined"
    screenAndSystemAudioRecording: Literal["authorized", "denied", "undetermined"] = "undetermined"

class EmployeeSystemPermissions(BaseModel):
    """Corresponds to IEmployeeSystemPermissions in the API documentation."""
    computer: str
    permissions: SystemPermissions
    createdAt: int = Field(default_factory=lambda: int(datetime.now().timestamp() * 1000))
    updatedAt: int = Field(default_factory=lambda: int(datetime.now().timestamp() * 1000))


# --- Schemas for Insightful-compatible Employee API ---

class EmployeeCreate(BaseModel):
    """Schema for the request body of POST /v1/employee."""
    name: str
    email: EmailStr

class EmployeeUpdate(BaseModel):
    """Schema for the request body of PUT /v1/employee/{id}."""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    title: Optional[str] = None

class EmployeeInDB(BaseModel):
    """
    Represents the full employee document as stored in our MongoDB.
    This combines the API model with our internal auth fields.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    name: str
    email: EmailStr
    accountId: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organizationId: str = "default-org" # Placeholder, can be configured
    identifier: EmailStr # Based on email for simplicity
    type: str = "personal" # Placeholder
    title: Optional[str] = None
    projects: List[str] = []
    systemPermissions: List[EmployeeSystemPermissions] = []
    createdAt: datetime = Field(default_factory=datetime.now)
    invited: datetime = Field(default_factory=datetime.now)
    
    # --- Fields from our custom auth flow ---
    hashed_password: Optional[str] = None
    is_active: bool = Field(default=False)
    activation_token: Optional[str] = None
    deactivated_at: Optional[datetime] = None

    class Config:
        # This allows Pydantic to correctly map MongoDB's `_id` field
        populate_by_name = True

class EmployeeResponse(BaseModel):
    """
    Schema for the response model returned by the Employee API, matching Insightful.
    """
    id: str
    name: str
    email: EmailStr
    accountId: str
    organizationId: str
    identifier: EmailStr
    type: str
    title: Optional[str] = None
    projects: List[str] = []
    systemPermissions: List[EmployeeSystemPermissions] = []
    
    is_active: bool = Field(default=False)
    createdAt: int
    invited: int
    deactivated_at: Optional[int] = None
    
    @classmethod
    def from_db_model(cls, db_model: EmployeeInDB) -> "EmployeeResponse":
        """Converts the DB model to the response model."""
        return cls(
            id=db_model.id,
            name=db_model.name,
            email=db_model.email,
            accountId=db_model.accountId,
            organizationId=db_model.organizationId,
            identifier=db_model.identifier,
            type=db_model.type,
            title=db_model.title,
            projects=db_model.projects,
            systemPermissions=db_model.systemPermissions,
            is_active=db_model.is_active,
            createdAt=int(db_model.createdAt.timestamp() * 1000),
            invited=int(db_model.invited.timestamp() * 1000),
            deactivated_at=int(db_model.deactivated_at.timestamp() * 1000) if db_model.deactivated_at else None
        )
