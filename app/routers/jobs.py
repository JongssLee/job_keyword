from fastapi import APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from app.database import job_db
from app.models.job import Job, JobDetails, PyObjectId
from typing import List, Optional, Dict

router = APIRouter(
    prefix="/jobs",
    tags=["jobs"],
)

def transform_job(job):
    if "_id" in job:
        job["_id"] = str(job["_id"])
    return job

@router.get("/", response_model=Dict[str, List[Job]])
async def get_all_jobs():
    kakao_jobs = await job_db["kakao_jobs"].find().to_list(1000)
    kakaopay_jobs = await job_db["kakaopay_jobs"].find().to_list(1000)
    all_jobs = {
        "카카오": [transform_job(job) for job in kakao_jobs],
        "카카오페이": [transform_job(job) for job in kakaopay_jobs]
    }
    if not all_jobs:
        raise HTTPException(status_code=404, detail="Jobs not found")
    return JSONResponse(content=jsonable_encoder(all_jobs))

@router.get("/{company}", response_model=List[Job])
async def get_jobs_by_company(company: str):
    if company.lower() == "kakao":
        jobs = await job_db["kakao_jobs"].find().to_list(1000)
    elif company.lower() == "kakaopay":
        jobs = await job_db["kakaopay_jobs"].find().to_list(1000)
    else:
        raise HTTPException(status_code=404, detail=f"No jobs found for company: {company}")
    
    if not jobs:
        raise HTTPException(status_code=404, detail=f"No jobs found for company: {company}")
    transformed_jobs = [transform_job(job) for job in jobs]
    return JSONResponse(content=jsonable_encoder(transformed_jobs))

@router.get("/search/{keyword}", response_model=List[Job])
async def get_jobs_by_keyword(keyword: str):
    query = {
        "$or": [
            {"직무내용": {"$elemMatch": {"$regex": keyword, "$options": "i"}}},
            {"공고제목": {"$regex": keyword, "$options": "i"}}
        ]
    }
    kakao_jobs = await job_db["kakao_jobs"].find(query).to_list(1000)
    kakaopay_jobs = await job_db["kakaopay_jobs"].find(query).to_list(1000)
    all_jobs = {
        "카카오": [transform_job(job) for job in kakao_jobs],
        "카카오페이": [transform_job(job) for job in kakaopay_jobs]
    }
    if not all_jobs:
        raise HTTPException(status_code=404, detail=f"No jobs found with keyword: {keyword}")
    transformed_jobs = [transform_job(job) for job in all_jobs]
    return JSONResponse(content=jsonable_encoder(all_jobs))
