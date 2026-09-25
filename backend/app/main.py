from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes.tenders import router as tenders_router
from app.api.routes.documents import router as documents_router

app = FastAPI(title=settings.app_name, version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/api/v1/health")
def health():
    return {"status": "ok", "service": "tender-intelligence-api", "version": "0.1.0"}

app.include_router(tenders_router, prefix="/api/v1")
app.include_router(documents_router, prefix="/api/v1")
