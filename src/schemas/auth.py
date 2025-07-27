from pydantic import BaseModel
from typing import Optional

class PasswordSet(BaseModel):
    """Schema for the user setting their password for the first time via an activation token."""
    token: str
    password: str

class Token(BaseModel):
    """Schema for the JWT access token returned to the client upon successful login."""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Schema for the data encoded within the JWT. This is internal to the application."""
    email: Optional[str] = None