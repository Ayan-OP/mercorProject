from typing import List, Optional

from db.mongo import get_db
from schemas.project import ProjectCreate, ProjectUpdate, ProjectInDB, ProjectPayroll


async def _validate_payroll(payroll: Optional[ProjectPayroll], assigned_employee_ids: List[str]):
    """
    A helper function to ensure payroll is only set for employees assigned to the project.
    
    Args:
        payroll: The payroll configuration to validate (can be None for optional updates)
        assigned_employee_ids: List of employee IDs currently assigned to the project
        
    Raises:
        ValueError: If payroll is set for an employee not assigned to the project
    """
    if payroll is None:
        return  # No payroll to validate
    
    payroll_dict = payroll.model_dump()
    for employee_id in payroll_dict.keys():
        if employee_id == '*':
            continue # Wildcard is always valid
        if employee_id not in assigned_employee_ids:
            raise ValueError(f"Cannot set payroll for employee '{employee_id}' who is not assigned to the project.")

async def _validate_active_employees(employee_ids: List[str]):
    """
    A helper function to ensure all provided employee IDs exist and are not deactivated.
    Raises a ValueError if any employee is invalid.
    """
    db = await get_db()
    if not employee_ids:
        return # Nothing to validate

    for employee_id in employee_ids:
        # Check if an employee exists with this ID and their 'deactivated' field is null
        employee = await db.employees.find_one({"_id": employee_id, "deactivated_at": None})
        if not employee:
            raise ValueError(f"Employee with ID '{employee_id}' is either deactivated or does not exist.")
        
async def _sync_employee_projects(project_id: str, added_ids: List[str], removed_ids: List[str]):
    """
    A helper function to update the 'projects' array in employee documents.
    """
    db = await get_db()
    if added_ids:
        await db.employees.update_many(
            {"_id": {"$in": added_ids}},
            {"$addToSet": {"projects": project_id}} # Use $addToSet to avoid duplicates
        )
    if removed_ids:
        await db.employees.update_many(
            {"_id": {"$in": removed_ids}},
            {"$pull": {"projects": project_id}}
        )

async def create_project( 
    project_in: ProjectCreate, 
    creator_id: str
) -> ProjectInDB:
    """
    Creates a new project record and updates the assigned employees' records.
    
    Args:
        project_in: The project creation data from the API request.
        creator_id: The ID of the user creating the project (from the auth token).
        
    Returns:
        The newly created project document.
    """
    db = await get_db()
    await _validate_active_employees(project_in.employees)
    
    # --- ADDED PAYROLL VALIDATION ---
    await _validate_payroll(project_in.payroll, project_in.employees)
    
    # Combine the input data with server-generated fields
    db_project = ProjectInDB(
        **project_in.model_dump(),
        creatorId=creator_id
    )
    
    # Convert to a dictionary for MongoDB, respecting the '_id' alias
    project_dict = db_project.model_dump(by_alias=True)
    
    await db.projects.insert_one(project_dict)
    
    # --- ADDED TWO-WAY BINDING ---
    # Add this new project's ID to each assigned employee's 'projects' list.
    if db_project.employees:
        await _sync_employee_projects(db_project.id, added_ids=db_project.employees, removed_ids=[])
    
    return db_project

async def get_project(project_id: str) -> Optional[ProjectInDB]:
    """
    Retrieves a single project by its ID.
    """
    db = await get_db()
    project_doc = await db.projects.find_one({"_id": project_id})
    if project_doc:
        return ProjectInDB(**project_doc)
    return None

async def get_projects() -> List[ProjectInDB]:
    """
    Retrieves a list of all non-archived projects.
    """
    db = await get_db()
    projects = []
    cursor = db.projects.find({"archived": False})
    async for document in cursor:
        projects.append(ProjectInDB(**document))
    return projects

async def update_project(
    project_id: str, 
    project_in: ProjectUpdate
) -> Optional[ProjectInDB]:
    """
    Updates a project's details and syncs employee assignments.
    """
    db = await get_db()
    # Get the current state of the project before updating
    current_project = await get_project(project_id)
    if not current_project:
        return None # Project doesn't exist
    
    # Determine the final list of employees for payroll validation
    final_employee_list = project_in.employees if project_in.employees is not None else current_project.employees

    # If the request includes a new list of employees, validate them and sync.
    if project_in.employees is not None:
        await _validate_active_employees(project_in.employees)
        
        # --- ADDED TWO-WAY BINDING LOGIC ---
        current_employee_ids = set(current_project.employees)
        new_employee_ids = set(project_in.employees)

        added_employees = list(new_employee_ids - current_employee_ids)
        removed_employees = list(current_employee_ids - new_employee_ids)
        
        await _sync_employee_projects(project_id, added_ids=added_employees, removed_ids=removed_employees)
        
    # --- ADDED PAYROLL VALIDATION ---
    if project_in.payroll is not None:
        await _validate_payroll(project_in.payroll, final_employee_list)

    # Get the data to update, excluding any fields that were not set in the request
    update_data = project_in.model_dump(exclude_unset=True)
    
    if not update_data:
        raise ValueError("No update data provided.")

    await db.projects.update_one(
        {"_id": project_id},
        {"$set": update_data}
    )
    
    # Return the updated document
    return await get_project(project_id)

async def delete_project(project_id: str) -> bool:
    """
    Permanently deletes a project and removes it from all assigned employees.
    """
    db = await get_db()
    # --- ADDED TWO-WAY BINDING ---
    # Before deleting the project, find out who was assigned to it
    project_to_delete = await get_project(project_id)
    if project_to_delete and project_to_delete.employees:
        # Remove the project ID from all assigned employees
        await _sync_employee_projects(project_id, added_ids=[], removed_ids=project_to_delete.employees)

    result = await db.projects.delete_one({"_id": project_id})
    return result.deleted_count > 0


