from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 운영 환경에서는 특정 도메인만 허용하도록 설정하세요
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB 설정
DB_URL = "mongodb://localhost:27017"
client = AsyncIOMotorClient(DB_URL)
job_db = client["job_database"]
user_db = client["user_database"]

kakao_collection = job_db["kakao_jobs"]
kakaopay_collection = job_db["kakaopay_jobs"]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")

class JobDetails(BaseModel):
    직군: Optional[str] = None
    신입_경력: Optional[str] = None
    근무형태: Optional[str] = None
    직무내용: Optional[List[str]] = None
    link: Optional[str] = None

class Job(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    title: str
    details: JobDetails

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }

def transform_job(job):
    if "_id" in job:
        job["_id"] = str(job["_id"])
    return job

@app.get("/jobs", response_model=Dict[str, List[Job]])
async def get_all_jobs():
    kakao_jobs = await kakao_collection.find().to_list(1000)
    kakaopay_jobs = await kakaopay_collection.find().to_list(1000)
    all_jobs = {
        "카카오": [transform_job(job) for job in kakao_jobs],
        "카카오페이": [transform_job(job) for job in kakaopay_jobs]
    }
    if not all_jobs:
        raise HTTPException(status_code=404, detail="Jobs not found")
    return JSONResponse(content=jsonable_encoder(all_jobs))

@app.get("/jobs/{company}", response_model=List[Job])
async def get_jobs_by_company(company: str):
    if company.lower() == "kakao":
        jobs = await kakao_collection.find().to_list(1000)
    elif company.lower() == "kakaopay":
        jobs = await kakaopay_collection.find().to_list(1000)
    else:
        raise HTTPException(status_code=404, detail=f"No jobs found for company: {company}")
    
    if not jobs:
        raise HTTPException(status_code=404, detail=f"No jobs found for company: {company}")
    transformed_jobs = [transform_job(job) for job in jobs]
    return JSONResponse(content=jsonable_encoder(transformed_jobs))

@app.get("/jobs/search/{keyword}", response_model=List[Job])
async def get_jobs_by_keyword(keyword: str):
    query = {
        "$or": [
            {"details.직무내용": {"$elemMatch": {"$regex": keyword, "$options": "i"}}},
            {"title": {"$regex": keyword, "$options": "i"}}
        ]
    }
    kakao_jobs = await kakao_collection.find(query).to_list(1000)
    kakaopay_jobs = await kakaopay_collection.find(query).to_list(1000)
    all_jobs = kakao_jobs + kakaopay_jobs
    
    if not all_jobs:
        raise HTTPException(status_code=404, detail=f"No jobs found with keyword: {keyword}")
    transformed_jobs = [transform_job(job) for job in all_jobs]
    return JSONResponse(content=jsonable_encoder(transformed_jobs))

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    password: str

@app.post("/users/")
async def create_user(user: UserCreate):
    if await user_db.users.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    if await user_db.users.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already taken")
    
    hashed_password = pwd_context.hash(user.password)
    
    user_data = user.dict()
    user_data["password"] = hashed_password
    result = await user_db.users.insert_one(user_data)
    
    return {"message": "User created successfully", "user_id": str(result.inserted_id)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
