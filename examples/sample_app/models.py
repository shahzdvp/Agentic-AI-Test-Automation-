
from pydantic import BaseModel, Field


class ItemCreate(BaseModel):
    """Schema for creating a new item."""
    title: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0)
    is_active: bool = True

class ItemUpdate(BaseModel):
    """Schema for updating an existing item."""
    title: str | None = Field(None, min_length=1, max_length=100)
    price: float | None = Field(None, gt=0)
    is_active: bool | None = None

class ItemResponse(ItemCreate):
    """Schema for an item response."""
    id: str

class LoginRequest(BaseModel):
    """Schema for a login request."""
    username: str
    password: str

class TokenResponse(BaseModel):
    """Schema for a token response."""
    access_token: str
    token_type: str = 'bearer'

class UserResponse(BaseModel):
    """Schema for a user response."""
    username: str
    email: str
