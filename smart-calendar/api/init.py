from fastapi import APIRouter
from api.routes_event import router as events_router
from api.routes_rag import router as rag_router

router = APIRouter()
router.include_router(events_router)
router.include_router(rag_router)
