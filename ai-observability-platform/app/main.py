# app/main.py
import uvicorn
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.telemetry import router as telemetry_router
# Import our new analytics router module
from app.api.v1.analytics import router as analytics_router
from app.api.v1.prompts import router as prompts_router
from app.core.database import init_db

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG
)

@app.on_event("startup")
def on_startup():
    init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register both sub-routers under our standard version prefix

app.include_router(telemetry_router, prefix=settings.API_V1_STR)
app.include_router(analytics_router, prefix=settings.API_V1_STR)
app.include_router(prompts_router, prefix=settings.API_V1_STR)

@app.get("/health", status_code=status.HTTP_200_OK, tags=["System Health"])
async def health_check():
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENV
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )