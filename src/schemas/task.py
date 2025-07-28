import uuid
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class TaskBase(BaseModel):
    """Base model for a task, containing fields from the request body."""
    name: str
    projectId: str
    description: Optional[str] = None
    billable: bool = True
    employees: List[str] = Field(default_factory=list)
    status: Optional[str] = "To Do"
    priority: Optional[str] = "Medium"

class TaskCreate(TaskBase):
    """Schema for creating a new task."""
    pass

class TaskUpdate(BaseModel):
    """Schema for updating an existing task. All fields are optional."""
    name: Optional[str] = None
    projectId: Optional[str] = None
    description: Optional[str] = None
    billable: Optional[bool] = None
    employees: Optional[List[str]] = None
    status: Optional[str] = None
    priority: Optional[str] = None

class TaskInDB(TaskBase):
    """Represents a task document as it is stored in MongoDB."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    creatorId: str # ID of the user who created the task
    organizationId: str = "default-org" # Placeholder
    createdAt: datetime = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True

class TaskResponse(BaseModel):
    """Schema for the response model returned by the API."""
    id: str
    name: str
    projectId: str
    description: Optional[str] = None
    billable: bool
    employees: List[str]
    status: str
    priority: str
    creatorId: str
    organizationId: str
    createdAt: int # Timestamp in milliseconds

    @classmethod
    def from_db_model(cls, db_model: TaskInDB) -> "TaskResponse":
        """Converts the DB model to the response model."""
        return cls(
            id=db_model.id,
            name=db_model.name,
            projectId=db_model.projectId,
            description=db_model.description,
            billable=db_model.billable,
            employees=db_model.employees,
            status=db_model.status,
            priority=db_model.priority,
            creatorId=db_model.creatorId,
            organizationId=db_model.organizationId,
            createdAt=int(db_model.createdAt.timestamp() * 1000)
        )
        
class TaskSummaryResponse(BaseModel):
    """
    A simplified response model for listing tasks, showing only key info.
    """
    id: str
    name: str
    projectId: str
    status: str
    priority: str
    employees: List[str] # Keep this so the desktop app knows who is assigned

    @classmethod
    def from_db_model(cls, db_model: TaskInDB) -> "TaskSummaryResponse":
        """Converts the DB model to the summary response model."""
        return cls(
            id=db_model.id,
            name=db_model.name,
            projectId=db_model.projectId,
            status=db_model.status,
            priority=db_model.priority,
            employees=db_model.employees
        )
