from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from core.security import create_access_token, get_current_active_employee
from schemas.auth import PasswordSet, Token
from schemas.employee import EmployeeInDB, EmployeeResponse
from services import employee_service

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/activate", response_model=EmployeeResponse)
async def activate_account(
    password_data: PasswordSet
):
    """
    Endpoint for the user to set their password using the token from their email.
    This activates their account.
    """
    try:
        activated_employee = await employee_service.activate_employee_account(password_data)
        return EmployeeResponse.from_db_model(activated_employee)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Login endpoint for the desktop app.
    Takes email (as username) and password. Returns a JWT.
    """
    user = await employee_service.authenticate_employee(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=EmployeeResponse)
async def read_users_me(
    current_user: EmployeeInDB = Depends(get_current_active_employee)
):
    """
    A protected endpoint to get the current user's details.
    Demonstrates how to use the authentication dependency. The desktop app
    would call this after login to get user info.
    """
    return EmployeeResponse.from_db_model(current_user)

