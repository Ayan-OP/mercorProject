from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from jose import JWTError, jwt

from core.config import settings
# Assuming TokenData is in a separate auth schema file
from schemas.auth import TokenData
from schemas.employee import EmployeeInDB
from services import employee_service


# --- JWT for Employee Login (Desktop App) ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def create_access_token(data: dict) -> str:
    """Creates a new JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


# --- Admin API Key Authentication (Backend Management) ---
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_admin_api_key(api_key: str = Security(api_key_header)):
    """
    A dependency to verify a static API key for admin-level access.
    The key is checked against the value in the .env file.
    """
    if not api_key or api_key != settings.ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing Admin API Key",
        )
    return api_key


# --- Employee Authentication Dependency (Desktop App) ---
async def get_current_active_employee(
    token: str = Depends(oauth2_scheme)
) -> EmployeeInDB:
    """
    A dependency to get the current employee from a JWT.
    Used to protect routes that the logged-in employee accesses.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        email: str = payload.get("sub")
        if not email:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    user = await employee_service.get_employee_by_email(email=token_data.email)
    if user is None or user.deactivated_at is not None:
        raise credentials_exception
    return user
