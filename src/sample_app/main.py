import uuid

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from sample_app.models import (
    ItemCreate,
    ItemResponse,
    ItemUpdate,
    LoginRequest,
    TokenResponse,
)

app = FastAPI(
    title="Sample REST API",
    description="A sample FastAPI application for testing purposes.",
    version="1.0.0"
)

# In-memory storage for items
ITEMS_DB: dict[str, dict] = {}

# Valid tokens for authentication
VALID_TOKENS = {'secret-token-123', 'admin-jwt-token'}

security = HTTPBearer()


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Verify that the provided bearer token is valid.
    
    Args:
        credentials: The HTTP authorization credentials containing the token.
        
    Returns:
        str: The validated token.
        
    Raises:
        HTTPException: If the token is invalid or missing.
    """
    if credentials.credentials not in VALID_TOKENS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials


@app.post("/api/v1/auth/login", response_model=TokenResponse)
def login(request: LoginRequest) -> TokenResponse:
    """
    Authenticate a user and return a JWT token.
    """
    if request.username == "admin" and request.password == "secretpassword":
        return TokenResponse(access_token="admin-jwt-token")

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
    )


@app.get("/api/v1/items", response_model=list[ItemResponse])
def list_items(token: str = Depends(verify_token)) -> list[ItemResponse]:
    """
    List all items. Requires authentication.
    """
    return [ItemResponse(id=item_id, **item_data) for item_id, item_data in ITEMS_DB.items()]


@app.post("/api/v1/items", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(item: ItemCreate, token: str = Depends(verify_token)) -> ItemResponse:
    """
    Create a new item. Requires authentication.
    """
    item_id = str(uuid.uuid4())
    item_dict = item.model_dump()
    ITEMS_DB[item_id] = item_dict
    return ItemResponse(id=item_id, **item_dict)


@app.get("/api/v1/items/{item_id}", response_model=ItemResponse)
def get_item(item_id: str, token: str = Depends(verify_token)) -> ItemResponse:
    """
    Get a single item by its ID. Requires authentication.
    """
    if item_id not in ITEMS_DB:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    return ItemResponse(id=item_id, **ITEMS_DB[item_id])


@app.put("/api/v1/items/{item_id}", response_model=ItemResponse)
def update_item(item_id: str, item_update: ItemUpdate, token: str = Depends(verify_token)) -> ItemResponse:
    """
    Update an existing item. Requires authentication.
    """
    if item_id not in ITEMS_DB:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )

    existing_item = ITEMS_DB[item_id]
    update_data = item_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        existing_item[key] = value

    ITEMS_DB[item_id] = existing_item
    return ItemResponse(id=item_id, **existing_item)


@app.delete("/api/v1/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: str, token: str = Depends(verify_token)) -> None:
    """
    Delete an item by its ID. Requires authentication.
    """
    if item_id not in ITEMS_DB:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )

    del ITEMS_DB[item_id]
    return None
