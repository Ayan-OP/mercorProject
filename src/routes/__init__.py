from .auth_router import router as authentication_router
from .employee_router import router as employeeData_router
from .system_permission_router import router as systemPermission_router
from .project_router import router as projectData_router

__all__ = [
    "authentication_router",
    "employeeData_router",
    "systemPermission_router",
    "projectData_router"
]