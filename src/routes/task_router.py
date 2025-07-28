from fastapi import APIRouter, Depends, HTTPException, status, Response, Query
from typing import List, Optional, Union

from core.security import get_admin_api_key, allow_admin_or_employee, get_admin_api_key_optional
from schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskSummaryResponse
from services import task_service

router = APIRouter(
    prefix="/v1/task",
    tags=["Tasks"]
)

@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_admin_api_key)])
async def add_task(
    task_in: TaskCreate,
    creator_id: str = "admin-user" # This would come from the auth token in a real system
):
    """
    Creates a new task.
    Matches: POST /v1/task
    """
    try:
        created_task_db = await task_service.create_task(task_in, creator_id)
        return TaskResponse.from_db_model(created_task_db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("", response_model=List[Union[TaskResponse, TaskSummaryResponse]], dependencies=[Depends(allow_admin_or_employee)])
async def find_tasks(
    projectId: Optional[str] = Query(None, alias="projectId"),
    admin_key: Optional[str] = Depends(get_admin_api_key_optional)
):
    """
    Retrieves a list of tasks for a given project.
    - Admins get the full task details.
    - Employees get a simplified summary view.
    """
    tasks_db = await task_service.get_tasks(
        project_id=projectId
    )
    if admin_key:
        return [TaskResponse.from_db_model(t) for t in tasks_db]
    # Otherwise, it's an employee, so return the summary response model
    return [TaskSummaryResponse.from_db_model(t) for t in tasks_db]

@router.get("/{task_id}", response_model=TaskResponse, dependencies=[Depends(allow_admin_or_employee)])
async def get_task(task_id: str):
    """
    Fetches a task by its provided ID.
    Matches: GET /v1/task/{id}
    """
    task_db = await task_service.get_task(task_id)
    if not task_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return TaskResponse.from_db_model(task_db)

@router.put("/{task_id}", response_model=TaskResponse, dependencies=[Depends(get_admin_api_key)])
async def update_task(
    task_id: str,
    task_in: TaskUpdate
):
    """
    Performs an update on a task specified by ID.
    Matches: PUT /v1/task/{id}
    """
    try:
        updated_task_db = await task_service.update_task(task_id, task_in)
        if not updated_task_db:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        return TaskResponse.from_db_model(updated_task_db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_admin_api_key)])
async def delete_task(task_id: str):
    """
    Deletes a task by its provided ID.
    Matches: DELETE /v1/task/{id}
    """
    success = await task_service.delete_task(task_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
