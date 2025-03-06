from fastapi import FastAPI, Request
from app.core.database import Base, engine
from app.core import redis_utils
from app.routers import task_router, ws_router, analytics_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio

def create_tables():
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Error creating tables: {str(e)}")

def get_application() -> FastAPI:
    create_tables()
    app = FastAPI(
        title="Real-Time Todo List",
        description="A FastAPI application with Redis caching, rate limiting, and real-time analytics.",
        version="1.0.0"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    async def startup_event():
        asyncio.create_task(redis_utils.monitor_redis())

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error occurred"}
        )

    app.include_router(task_router.router)
    app.include_router(ws_router.router)
    app.include_router(analytics_router.router)
    return app

app = get_application()