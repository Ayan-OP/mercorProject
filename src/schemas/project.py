from pydantic import BaseModel, Field, RootModel
from typing import Optional, List, Dict
import uuid
from datetime import datetime

# --- Sub-models based on the API documentation ---

class ScreenshotSettings(BaseModel):
    """Settings for screenshots on a project."""
    screenshotEnabled: bool

class Payroll(BaseModel):
    """Payroll details for an employee on a project."""
    billRate: float
    overtimeBillRate: Optional[float] = None

class ProjectPayroll(RootModel[Dict[str, Payroll]]):
    """
    A dictionary mapping an employeeId (or '*' for all) to their payroll details.
    Uses RootModel for complex dictionary mappings in Pydantic v2.
    """

# --- Main Project Schemas ---

class ProjectBase(BaseModel):
    """Base model with fields common to the Insightful Project model."""
    name: str
    description: Optional[str] = None
    billable: bool = True
    employees: List[str] = Field(default_factory=list)
    screenshotSettings: ScreenshotSettings
    payroll: ProjectPayroll

class ProjectCreate(ProjectBase):
    """Schema for creating a new project. creatorId will be added from the token."""
    pass

class ProjectUpdate(BaseModel):
    """Schema for updating an existing project. All fields are optional."""
    name: Optional[str] = None
    description: Optional[str] = None
    billable: Optional[bool] = None
    employees: Optional[List[str]] = None
    screenshotSettings: Optional[ScreenshotSettings] = None
    payroll: Optional[ProjectPayroll] = None
    archived: Optional[bool] = None

class ProjectInDB(ProjectBase):
    """Represents a project document as it is stored in MongoDB."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    creatorId: str # ID of the admin/user who created the project
    organizationId: str = "default-org" # Placeholder
    archived: bool = False
    statuses: List[str] = ["To Do", "In Progress", "Done"] # Default statuses
    priorities: List[str] = ["Low", "Medium", "High"] # Default priorities
    createdAt: datetime = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True

class ProjectResponse(BaseModel):
    """Schema for the response model returned by the API."""
    id: str
    name: str
    description: Optional[str] = None
    billable: bool
    employees: List[str]
    screenshotSettings: ScreenshotSettings
    payroll: ProjectPayroll
    creatorId: str
    organizationId: str
    archived: bool
    statuses: List[str]
    priorities: List[str]
    createdAt: int # Timestamp in milliseconds

    @classmethod
    def from_db_model(cls, db_model: ProjectInDB) -> "ProjectResponse":
        """Converts the DB model to the response model."""
        return cls(
            id=db_model.id,
            name=db_model.name,
            description=db_model.description,
            billable=db_model.billable,
            employees=db_model.employees,
            screenshotSettings=db_model.screenshotSettings,
            payroll=db_model.payroll,
            creatorId=db_model.creatorId,
            organizationId=db_model.organizationId,
            archived=db_model.archived,
            statuses=db_model.statuses,
            priorities=db_model.priorities,
            createdAt=int(db_model.createdAt.timestamp() * 1000)
        )
        
class ProjectSummaryResponse(BaseModel):
    """
    A simplified response model for listing tasks, showing only key info.
    """
    id: str
    name: str
    description: Optional[str] = None
    billable: bool
    employees: List[str]
    archived: bool
    statuses: List[str]
    priorities: List[str]

    @classmethod
    def from_db_model(cls, db_model: ProjectInDB) -> "ProjectSummaryResponse":
        """Converts the DB model to the summary response model."""
        return cls(
            id=db_model.id,
            name=db_model.name,
            description=db_model.description,
            billable=db_model.billable,
            employees=db_model.employees,
            archived=db_model.archived,
            statuses=db_model.statuses,
            priorities=db_model.priorities,
        )
