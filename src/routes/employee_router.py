from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

# We will use a new dependency for admin-level API key auth
from core.security import get_admin_api_key
from schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeResponse
from services import employee_service

router = APIRouter(
    prefix="/v1/employee",
    tags=["Employees"],
    # This dependency now protects all routes with an admin API key
    dependencies=[Depends(get_admin_api_key)]
)

@router.post("", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee_route(
    employee_in: EmployeeCreate
):
    """
    Creates a new employee and sends an invitation email.
    Matches: POST /v1/employee
    """
    try:
        created_employee = await employee_service.create_employee(employee_in)
        return EmployeeResponse.from_db_model(created_employee)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("", response_model=List[EmployeeResponse])
async def list_employees_route():
    """
    Retrieves a list of all employees in the organization.
    Matches: GET /v1/employee
    """
    employees = await employee_service.get_employees()
    return [EmployeeResponse.from_db_model(emp) for emp in employees]

@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee_route(employee_id: str):
    """
    Fetches a single employee by their ID.
    Matches: GET /v1/employee/{id}
    """
    employee = await employee_service.get_employee(employee_id)
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return EmployeeResponse.from_db_model(employee)

@router.put("/{employee_id}", response_model=EmployeeResponse)
async def update_employee_route(
    employee_id: str,
    employee_in: EmployeeUpdate
):
    """
    Performs an update on an employee specified by ID.
    Matches: PUT /v1/employee/{id}
    """
    try:
        updated_employee = await employee_service.update_employee(employee_id, employee_in)
        if not updated_employee:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
        return EmployeeResponse.from_db_model(updated_employee)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/{employee_id}/deactivate", response_model=EmployeeResponse)
async def deactivate_employee_route(employee_id: str):
    """
    Deactivates an employee by their ID.
    Matches: POST /v1/employee/{id}/deactivate
    """
    try:
        deactivated_employee = await employee_service.deactivate_employee(employee_id)
        if not deactivated_employee:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
        return EmployeeResponse.from_db_model(deactivated_employee)
    except ValueError as e:
        # This handles the case where the employee is already deactivated
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

