from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from db.mongo import get_db
from schemas.time_entry import TimeWindowCreate, TimeWindowInDB, TimeWindowUpdate
from . import project_service, task_service, employee_service

async def _validate_time_window(window_in: TimeWindowCreate, employee_id: str):
    """
    Helper function to validate data for a new time window.
    - Ensures the employee, project, and task exist and are active/assigned.
    """
    # 1. Check if the employee is active
    employee = await employee_service.get_employee(employee_id)
    if not employee or employee.deactivated_at:
        raise ValueError("Employee is not active or does not exist.")

    # 2. Check if the project exists and the employee is assigned to it
    project = await project_service.get_project(window_in.projectId)
    if not project or project.archived:
        raise ValueError("Project does not exist or is archived.")
    if employee_id not in project.employees:
        raise ValueError("Employee is not assigned to this project.")

    # 3. Check if the task exists and the employee is assigned to it
    task = await task_service.get_task(window_in.taskId)
    if not task:
        raise ValueError("Task does not exist.")
    if employee_id not in task.employees:
        raise ValueError("Employee is not assigned to this task.")


async def add_time_window(
    window_in: TimeWindowCreate, 
    employee_id: str
) -> TimeWindowInDB:
    """
    Creates a new time window record in the database.
    This is called by the desktop app to submit a chunk of tracked time.
    """
    db = await get_db()
    await _validate_time_window(window_in, employee_id)

    # Convert millisecond timestamps to datetime objects
    start_time = datetime.fromtimestamp(window_in.start / 1000.0)
    end_time = datetime.fromtimestamp(window_in.end / 1000.0)
    
    # Calculate translated times
    start_translated = window_in.start - window_in.timezoneOffset
    end_translated = window_in.end - window_in.timezoneOffset

    db_window = TimeWindowInDB(
        **window_in.model_dump(),
        employeeId=employee_id,
        startTime=start_time,
        endTime=end_time,
        startTranslated=start_translated,
        endTranslated=end_translated
    )
    
    window_dict = db_window.model_dump(by_alias=True)
    await db.time_windows.insert_one(window_dict)
    
    return db_window

async def get_time_windows(
    start: int, 
    end: int, 
    employee_id: Optional[str] = None
) -> List[TimeWindowInDB]:
    """
    Retrieves a list of time windows within a given date range.
    Optionally filters by a specific employee.
    """
    db = await get_db()
    start_dt = datetime.fromtimestamp(start / 1000.0)
    end_dt = datetime.fromtimestamp(end / 1000.0)

    query = {
        "startTime": {"$gte": start_dt},
        "endTime": {"$lte": end_dt}
    }
    if employee_id:
        query["employeeId"] = employee_id

    windows = []
    cursor = db.time_windows.find(query)
    async for document in cursor:
        windows.append(TimeWindowInDB(**document))
    return windows

async def update_time_windows(
    update_data: TimeWindowUpdate,
    employee_id: Optional[str] = None,
    project_id: Optional[str] = None
) -> int:
    """
    Performs a bulk update on time windows based on employee and/or project ID.
    Returns the number of documents modified.
    """
    db = await get_db()
    if not employee_id and not project_id:
        raise ValueError("Either employee_id or project_id must be provided.")

    query: Dict[str, Any] = {}
    if employee_id:
        query["employeeId"] = employee_id
    if project_id:
        query["projectId"] = project_id

    update_payload = {"$set": update_data.model_dump(exclude_unset=True)}
    
    if not update_payload["$set"]:
        raise ValueError("No update data provided.")

    result = await db.time_windows.update_many(query, update_payload)
    return result.modified_count