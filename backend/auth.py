from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(tags=["Authentication"])
print("✅ auth.py imported")

class LoginRequest(BaseModel):
    username: str
    password: str


# Temporary admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


@router.post("/login")
def login(data: LoginRequest):

    if (
        data.username == ADMIN_USERNAME
        and data.password == ADMIN_PASSWORD
    ):
        return {
            "success": True,
            "message": "Login successful",
            "username": ADMIN_USERNAME,
        }

    raise HTTPException(
        status_code=401,
        detail="Invalid username or password",
    )