from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from app.database import user_db
from app.models.user import User, UserInDB
from app.schemas.user import User as UserSchema
from app.utils.auth import get_current_user
from typing import List, Optional

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

class KeywordUpdate(BaseModel):
    keywords: List[str]

@router.post("/")
async def create_user(user: UserCreate):
    if await user_db.users.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    if await user_db.users.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already taken")
    
    hashed_password = pwd_context.hash(user.password)
    
    user_data = user.dict()
    user_data["hashed_password"] = hashed_password
    user_data["keywords"] = []
    del user_data["password"]
    result = await user_db.users.insert_one(user_data)
    
    return {"message": "User created successfully", "user_id": str(result.inserted_id)}

@router.put("/keywords", response_model=UserSchema)
async def update_keywords(keywords: KeywordUpdate, current_user: UserInDB = Depends(get_current_user)):
    await user_db.users.update_one(
        {"username": current_user.username},
        {"$set": {"keywords": keywords.keywords}}
    )
    updated_user = await user_db.users.find_one({"username": current_user.username})
    return updated_user
