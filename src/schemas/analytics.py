from pydantic import BaseModel, RootModel
from typing import List

class ProjectTime(BaseModel):
    """
    Represents the aggregated time and financial data for a single project
    over a specified period.
    """
    id: str # Project Id
    time: int # Total time in milliseconds
    costs: float
    income: float

class ProjectTimeResponse(RootModel[List[ProjectTime]]):
    """
    The response model for the project time analytics endpoint, which is a list
    of ProjectTime objects.
    """
    
class TaskTime(BaseModel):
    """
    Represents the total time an employee has spent on a specific task.
    """
    employeeId: str
    taskId: str
    totalTimeMillis: int