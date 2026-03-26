from fastapi import APIRouter

from app.api.routes import router as analyze_router

router = APIRouter()
router.include_router(analyze_router)
