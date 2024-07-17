from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 운영 환경에서는 특정 도메인만 허용하도록 설정하세요
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB 연결 설정
DB_URL = "mongodb://localhost:27017"
DB_NAME = "user_database"
client = AsyncIOMotorClient(DB_URL)
db = client[DB_NAME]

# 비밀번호 해싱을 위한 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserCreate(BaseModel):
    username: str
    email: str
    full_name: str
    password: str

@app.post("/users/")
async def create_user(user: UserCreate):
    # 이메일 중복 체크
    if await db.users.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 사용자 이름 중복 체크
    if await db.users.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # 비밀번호 해싱
    hashed_password = pwd_context.hash(user.password)
    
    # 사용자 정보 저장
    user_data = user.dict()
    user_data["password"] = hashed_password
    result = await db.users.insert_one(user_data)
    
    return {"message": "User created successfully", "user_id": str(result.inserted_id)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)