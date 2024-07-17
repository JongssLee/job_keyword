from fastapi import APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from app.database import user_db
from typing import List, Optional, Dict

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    password: str

@router.post("/")
async def create_user(user: UserCreate):
    if await user_db.users.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    if await user_db.users.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already taken")
    
    hashed_password = pwd_context.hash(user.password)
    
    user_data = user.dict()
    user_data["hashed_password"] = hashed_password
    del user_data["password"]
    result = await user_db.users.insert_one(user_data)
    
    return {"message": "User created successfully", "user_id": str(result.inserted_id)}
