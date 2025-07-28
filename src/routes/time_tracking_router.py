from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional

from core.security import get_current_active_employee, get_admin_api_key
from schemas.employee import EmployeeInDB
from schemas.time_entry import TimeWindowCreate, TimeWindowResponse, TimeWindowUpdate
from services.time_tracking_service import add_time_window, update_time_windows

router = APIRouter(
    prefix="/v1/time-entries",
    tags=["Time Tracking"],
)

@router.post("", response_model=TimeWindowResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_active_employee)])
async def submit_time_window(
    window_in: TimeWindowCreate,
    current_user: EmployeeInDB = Depends(get_current_active_employee)
):
    """
    Endpoint for the desktop app to submit a tracked time window.
    """
    try:
        # The employee's ID is securely taken from their authentication token
        created_window = await add_time_window(
            window_in, employee_id=current_user.id
        )
        return created_window
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
@router.put("/update", status_code=status.HTTP_200_OK, dependencies=[Depends(get_admin_api_key)])
async def bulk_update_time_windows(
    update_data: TimeWindowUpdate,
    employeeId: Optional[str] = Query(None, alias="employeeId"),
    projectId: Optional[str] = Query(None, alias="projectId")
):
    """
    Admin endpoint to bulk-update time windows.
    Must provide at least one filter (employeeId or projectId).
    """
    try:
        modified_count = await update_time_windows(
            update_data=update_data,
            employee_id=employeeId,
            project_id=projectId
        )
        return {"message": "Update successful", "modified_count": modified_count}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

