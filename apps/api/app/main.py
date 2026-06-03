from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import routers
from app.core.config import get_settings
from app.core.database import Base, engine
from app.core.security import hash_password
from app.core.database import SessionLocal
from app.models.entities import User
from app.models import entities  # noqa: F401


settings = get_settings()
app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        exists = db.query(User).filter(User.email == settings.admin_email).first()
        if not exists:
            db.add(User(email=settings.admin_email, hashed_password=hash_password(settings.admin_password), role="admin"))
            db.commit()
    finally:
        db.close()


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": "health-live-source-diagnostics-2026-06-03",
        "api_prefix": settings.api_prefix,
        "enable_live_sources": settings.enable_live_sources,
        "amazon_data_provider": settings.amazon_data_provider,
        "rainforest_key_configured": bool(settings.rainforest_api_key),
        "rainforest_ready": bool(
            settings.enable_live_sources
            and settings.amazon_data_provider.lower().strip() == "rainforest"
            and settings.rainforest_api_key
        ),
    }


for router in routers:
    app.include_router(router, prefix=settings.api_prefix)
