import uuid
from db.mongo import get_db
from typing import List, Optional
from bson import ObjectId
from datetime import datetime, timezone

from schemas.auth import PasswordSet
from schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeInDB, EmployeeSystemPermissions
from helpers.email_helper import send_invitation_email
from helpers.password_helpers import get_password_hash, verify_password


async def get_employee_by_email(email: str) -> Optional[EmployeeInDB]:
    """
    Retrieves an employee from the database by their email.
    """
    db = await get_db()
    employee_doc = await db.employees.find_one({"email": email})
    if employee_doc:
        return EmployeeInDB(**employee_doc)
    return None

async def create_employee(employee_in: EmployeeCreate) -> EmployeeInDB:
    """
    Creates a new employee record and triggers the invitation email flow.
    """
    if await get_employee_by_email(employee_in.email):
        raise ValueError("Employee with this email already exists.")

    activation_token = str(uuid.uuid4())
    
    # Create the full employee document based on our DB schema
    db_employee = EmployeeInDB(
        name=employee_in.name,
        email=employee_in.email,
        identifier=employee_in.email,
        activation_token=activation_token
    )

    # Convert to dict, using aliases (for _id)
    employee_dict = db_employee.model_dump(by_alias=True)
    db = await get_db()
    await db.employees.insert_one(employee_dict)
    
    # Send the invitation email
    await send_invitation_email(to_email=db_employee.email, token=activation_token)

    return db_employee

async def get_employee(employee_id: str) -> Optional[EmployeeInDB]:
    """Retrieves a single employee by their ID."""
    db = await get_db()
    employee_doc = await db.employees.find_one({"_id": employee_id})
    if employee_doc:
        return EmployeeInDB(**employee_doc)
    return None

async def get_employees() -> List[EmployeeInDB]:
    """Retrieves a list of all employees."""
    employees = []
    db = await get_db()
    cursor = db.employees.find()
    async for document in cursor:
        employees.append(EmployeeInDB(**document))
    return employees

async def update_employee(employee_id: str, employee_in: EmployeeUpdate) -> Optional[EmployeeInDB]:
    """Updates an employee's details."""
    update_data = employee_in.model_dump(exclude_unset=True)
    
    if not update_data:
        raise ValueError("No update data provided.")

    db = await get_db()
    await db.employees.update_one(
        {"_id": employee_id},
        {"$set": update_data}
    )
    
    return await get_employee(employee_id)

async def deactivate_employee(employee_id: str) -> Optional[EmployeeInDB]:
    """
    Deactivates an employee and removes them from all assigned projects.
    """
    db = await get_db()
    employee = await get_employee(employee_id)
    if not employee:
        return None # Employee not found
    
    if employee.deactivated_at:
        raise ValueError("Employee is already deactivated.")

    # Before deactivating, if the employee is assigned to any projects...
    if employee.projects:
        # ...remove this employee's ID from the 'employees' array of all those projects.
        await db.projects.update_many(
            {"_id": {"$in": employee.projects}},
            {"$pull": {"employees": employee_id}}
        )

    # Now, proceed with deactivating the employee
    await db.employees.update_one(
        {"_id": employee_id},
        {"$set": {
            "deactivated_at": datetime.now(timezone.utc),
            "is_active": False # Explicitly set is_active to False
        }}
    )
    
    return await get_employee(employee_id)

async def activate_employee_account(password_data: PasswordSet) -> EmployeeInDB:
    """
    Activates an employee's account by verifying their token and setting their password.
    This is called by the /auth/activate route.
    """
    db = await get_db()
    employee_doc = await db.employees.find_one({"activation_token": password_data.token, "is_active": False})
    
    if not employee_doc:
        raise ValueError("Invalid or expired activation token.")

    hashed_password = get_password_hash(password_data.password)
    
    await db.employees.update_one(
        {"_id": employee_doc["_id"]},
        {
            "$set": {
                "hashed_password": hashed_password,
                "is_active": True,
                "activation_token": None  # Invalidate the token after use
            }
        }
    )

    activated_employee = await db.employees.find_one({"_id": employee_doc["_id"]})
    return EmployeeInDB(**activated_employee)


async def authenticate_employee(email: str, password: str) -> Optional[EmployeeInDB]:
    """
    Authenticates an employee by email and password for the desktop app login.
    This is called by the /auth/login route.
    """
    employee = await get_employee_by_email(email)
    if not employee:
        return None # User does not exist
    if not employee.is_active or not employee.hashed_password:
        return None # Account exists but is not active
    if not verify_password(password, employee.hashed_password):
        return None # Incorrect password
        
    return employee

async def update_system_permissions(
    employee_id: str, 
    permissions_in: EmployeeSystemPermissions
) -> Optional[EmployeeInDB]:
    """
    Updates or adds system permissions for a specific computer for an employee.
    This is called by the desktop app.
    """
    db = await get_db()
    # Find the employee first
    employee = await get_employee(employee_id)
    if not employee:
        return None

    # Check if permissions for this computer already exist
    existing_permission_index = -1
    for i, p in enumerate(employee.systemPermissions):
        if p.computer == permissions_in.computer:
            existing_permission_index = i
            break
    
    if existing_permission_index != -1:
        # If it exists, update it in the array
        query = {"$set": {f"systemPermissions.{existing_permission_index}": permissions_in.model_dump()}}
    else:
        # If it doesn't exist, add it to the array
        query = {"$push": {"systemPermissions": permissions_in.model_dump()}}

    await db.employees.update_one({"_id": employee_id}, query)

    return await get_employee(employee_id)
