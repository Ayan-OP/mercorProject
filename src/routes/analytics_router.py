from fastapi import APIRouter, Depends, Query, status, HTTPException
from typing import List, Optional

from core.security import get_admin_api_key, get_admin_api_key_optional, get_current_active_employee_optional, allow_admin_or_employee
from schemas.analytics import ProjectTimeResponse, TaskTime
from schemas.time_entry import TimeWindowResponse
from schemas.employee import EmployeeInDB
from services import time_tracking_service, analytics_service

router = APIRouter(
    prefix="/v1/analytics",
    tags=["Analytics"]
)

@router.get("/window", response_model=List[TimeWindowResponse], dependencies=[Depends(get_admin_api_key)])
async def get_app_analytics(
    start: int,
    end: int,
    employeeId: Optional[str] = Query(None, alias="employeeId")
):
    """
    Get app analytics by retrieving time windows within a date range.
    Matches: GET /v1/analytics/window
    """
    windows_db = await time_tracking_service.get_time_windows(
        start=start, end=end, employee_id=employeeId
    )
    return windows_db

@router.get("/project-time", response_model=ProjectTimeResponse, dependencies=[Depends(get_admin_api_key)])
async def get_project_time(
    start: int,
    end: int,
    employeeId: Optional[str] = Query(None, alias="employeeId"),
    projectId: Optional[str] = Query(None, alias="projectId"),
    taskId: Optional[str] = Query(None, alias="taskId")
):
    """
    Get aggregated project time analytics within a date range.
    Matches: GET /v1/analytics/project-time
    """
    project_time_data = await analytics_service.get_project_time_analytics(
        start=start,
        end=end,
        employee_id=employeeId,
        project_id=projectId,
        task_id=taskId
    )
    return project_time_data

@router.get("/task-time", response_model=TaskTime, dependencies=[Depends(allow_admin_or_employee)])
async def get_task_time(
    employeeId: str = Query(..., alias="employeeId"),
    taskId: str = Query(..., alias="taskId"),
    admin_key: Optional[str] = Depends(get_admin_api_key_optional),
    current_user: Optional[EmployeeInDB] = Depends(get_current_active_employee_optional)
):
    """
    Get total time spent by a specific employee on a specific task.
    - Admins can query for any employee.
    - Employees can only query for their own time.
    """
    # Security check: If the requester is an employee, they can only query their own ID.
    if not admin_key and current_user:
        if current_user.id != employeeId:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this data."
            )

    task_time_data = await analytics_service.get_task_time_for_employee(
        employee_id=employeeId,
        task_id=taskId
    )
    
    if task_time_data is None:
        # This case is handled in the service, but as a fallback:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No time found for this employee and task.")

    return task_time_data

