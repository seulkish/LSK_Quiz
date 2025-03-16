from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import quiz, submission, user
from app.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="퀴즈 응시 시스템 API",
    version="1.0.0",
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(quiz.router, prefix=settings.API_PREFIX)
app.include_router(submission.router, prefix=settings.API_PREFIX)
app.include_router(user.router, prefix=settings.API_PREFIX)

@app.get("/")
async def root():
    return {"message": "퀴즈 응시 시스템에 오신 것을 환영합니다."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)