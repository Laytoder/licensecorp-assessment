from fastapi import FastAPI
from app.core.database import Base, engine
from app.routers import task_router, ws_router, analytics_router

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_application() -> FastAPI:
    create_tables()
    app = FastAPI(
        title="Real-Time Todo List",
        description="A FastAPI application with Redis caching, TTL-based task expiry, rate limiting, and real-time analytics.",
        version="1.0.0"
    )
    app.include_router(task_router.router)
    app.include_router(ws_router.router)
    app.include_router(analytics_router.router)
    return app

app = get_application()