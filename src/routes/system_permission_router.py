from fastapi import APIRouter, Depends, HTTPException, status

from core.security import get_current_active_employee
from schemas.employee import EmployeeSystemPermissions, EmployeeResponse, EmployeeInDB
from services import employee_service

router = APIRouter(
    prefix="/v1/employee",
    tags=["System Permissions"],
    # This dependency protects the route with the employee's JWT
    dependencies=[Depends(get_current_active_employee)]
)

@router.post("/{employee_id}/permissions", response_model=EmployeeResponse)
async def update_employee_permissions_route(
    employee_id: str,
    permissions_in: EmployeeSystemPermissions,
    current_user: EmployeeInDB = Depends(get_current_active_employee)
):
    """
    Endpoint for the desktop app to send its system permissions.
    It's authenticated by the employee's JWT, and we ensure an employee
    can only update their own permissions.
    """
    # Security Check: Ensure the logged-in user (from token) can only update their own record
    if current_user.id != employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action."
        )

    updated_employee = await employee_service.update_system_permissions(employee_id, permissions_in)
    
    if not updated_employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")

    return EmployeeResponse.from_db_model(updated_employee)
