from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import users, jobs, auth

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 운영 환경에서는 특정 도메인만 허용하도록 설정하세요
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(users.router)
app.include_router(jobs.router)
app.include_router(auth.router)
