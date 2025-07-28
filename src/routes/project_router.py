from fastapi import APIRouter, Depends, HTTPException, status, Response
from typing import List, Optional, Union

from core.security import get_admin_api_key, allow_admin_or_employee, get_admin_api_key_optional
from schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectSummaryResponse
from services import project_service

router = APIRouter(
    prefix="/v1/project",
    tags=["Projects"]
)

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_admin_api_key)])
async def add_project(
    project_in: ProjectCreate,
    creator_id: str = "admin-user"
):
    """
    Creates a new project in your organization.
    Matches: POST /v1/project
    """
    created_project_db = await project_service.create_project(project_in, creator_id)
    return ProjectResponse.from_db_model(created_project_db)

@router.get("", response_model=List[ProjectResponse], dependencies=[Depends(get_admin_api_key)])
async def find_projects():
    """
    Retrieves tasks.
    - If called by an admin, returns all projects.
    """
    projects_db = await project_service.get_projects()
    return [ProjectResponse.from_db_model(p) for p in projects_db]

@router.get("/{project_id}", response_model=Union[ProjectResponse, ProjectSummaryResponse], dependencies=[Depends(allow_admin_or_employee)])
async def get_project(
    project_id: str, 
    admin_key: Optional[str] = Depends(get_admin_api_key_optional)
):
    """
    Fetches a project by its provided ID.
    Matches: GET /v1/project/{id}
    """
    project_db = await project_service.get_project(project_id)
    if not project_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if admin_key:
        return ProjectResponse.from_db_model(project_db)
    return ProjectSummaryResponse.from_db_model(project_db)

@router.put("/{project_id}", response_model=ProjectResponse, dependencies=[Depends(get_admin_api_key)])
async def update_project(
    project_id: str,
    project_in: ProjectUpdate
):
    """
    Performs an update on a project specified by ID.
    Matches: PUT /v1/project/{id}
    """
    try:
        updated_project_db = await project_service.update_project(project_id, project_in)
        if not updated_project_db:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        return ProjectResponse.from_db_model(updated_project_db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_admin_api_key)])
async def delete_project(project_id: str):
    """
    Deletes a project by its provided ID.
    Matches: DELETE /v1/project/{id}
    """
    success = await project_service.delete_project(project_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    # Return a 204 No Content response, which is standard for successful deletions
    return Response(status_code=status.HTTP_204_NO_CONTENT)

