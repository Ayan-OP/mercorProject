from typing import List, Optional

from db.mongo import get_db
from schemas.task import TaskCreate, TaskUpdate, TaskInDB
from services import project_service # To validate project existence and employee assignments

async def _validate_task_data(project_id: str, employee_ids: List[str]):
    """
    Helper function to validate data before creating or updating a task.
    - Ensures the parent project exists.
    - Ensures employees assigned to the task are also assigned to the parent project.
    """
    # 1. Check if the project exists
    project = await project_service.get_project(project_id)
    if not project:
        raise ValueError(f"Project with ID '{project_id}' does not exist.")

    # 2. Check if employees assigned to the task are part of the project
    if employee_ids:
        project_employee_set = set(project.employees)
        for employee_id in employee_ids:
            if employee_id not in project_employee_set:
                raise ValueError(
                    f"Employee with ID '{employee_id}' cannot be assigned to the task "
                    f"as they are not assigned to the parent project."
                )

async def create_task( 
    task_in: TaskCreate, 
    creator_id: str
) -> TaskInDB:
    """
    Creates a new task record in the database.
    """
    db = await get_db()
    await _validate_task_data(task_in.projectId, task_in.employees)
    
    db_task = TaskInDB(
        **task_in.model_dump(),
        creatorId=creator_id
    )
    
    task_dict = db_task.model_dump(by_alias=True)
    await db.tasks.insert_one(task_dict)
    
    return db_task

async def get_task(task_id: str) -> Optional[TaskInDB]:
    """
    Retrieves a single task by its ID.
    """
    db = await get_db()
    task_doc = await db.tasks.find_one({"_id": task_id})
    if task_doc:
        return TaskInDB(**task_doc)
    return None

async def get_tasks(
    project_id: Optional[str] = None 
) -> List[TaskInDB]:
    """
    Retrieves a list of all tasks.
    """
    db = await get_db()
    query = {}
    if project_id:
        query["projectId"] = project_id
    tasks = []
    cursor = db.tasks.find(query)
    async for document in cursor:
        tasks.append(TaskInDB(**document))
    return tasks

async def update_task(
    task_id: str, 
    task_in: TaskUpdate
) -> Optional[TaskInDB]:
    """
    Updates a task's details with proper validation.
    """
    db = await get_db()
    # First, get the current state of the task
    current_task = await get_task(task_id)
    if not current_task:
        return None # Task not found

    # Determine the final state of the task after the update
    # This allows us to validate the complete, final object
    updated_data = task_in.model_dump(exclude_unset=True)
    final_task_data = current_task.model_copy(update=updated_data)

    # Now, perform validation on the final state
    await _validate_task_data(final_task_data.projectId, final_task_data.employees)

    if not updated_data:
        raise ValueError("No update data provided.")

    await db.tasks.update_one(
        {"_id": task_id},
        {"$set": updated_data}
    )
    
    return await get_task(task_id)

async def delete_task(task_id: str) -> bool:
    """
    Permanently deletes a task from the database.
    """
    db = await get_db()
    result = await db.tasks.delete_one({"_id": task_id})
    return result.deleted_count > 0
