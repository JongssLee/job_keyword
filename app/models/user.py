from pydantic import BaseModel, EmailStr
from typing import Optional, List

class User(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    keywords: List[str] = []

class UserInDB(User):
    hashed_password: str
