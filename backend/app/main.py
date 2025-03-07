from fastapi import FastAPI, Request
from app.core.database import Base, engine
from app.core import redis_utils
from app.routers import task_router, ws_router, analytics_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import datetime

# Track the Redis monitoring task to prevent garbage collection
redis_monitor_task = None

print("ran")

def create_tables():
    try:
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully")
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
        allow_origins=["http://localhost:8080", "http://localhost:3001", "http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    async def startup_event():
        global redis_monitor_task
        print(f"[{datetime.datetime.now()}] Application starting up - initializing Redis monitoring task")
        
        # Sync analytics counters from database to Redis
        from app.core.database import SessionLocal
        from app.services.analytics_service import AnalyticsService
        
        db = SessionLocal()
        try:
            AnalyticsService.ensure_counters_synced(db)
        finally:
            db.close()
        
        # Explicitly create the task and store it in a global variable to prevent garbage collection
        redis_monitor_task = asyncio.create_task(redis_utils.monitor_redis())
        # Add a done callback to log when the task completes (if it ever does)
        redis_monitor_task.add_done_callback(
            lambda t: print(f"[{datetime.datetime.now()}] Redis monitoring task ended: {t.exception() if t.exception() else 'No exception'}")
        )
        
        print(f"[{datetime.datetime.now()}] Redis monitoring task created successfully")

    @app.on_event("shutdown")
    async def shutdown_event():
        global redis_monitor_task
        print(f"[{datetime.datetime.now()}] Application shutting down - cleaning up tasks")
        
        # Cancel the Redis monitoring task
        if redis_monitor_task:
            redis_monitor_task.cancel()
            try:
                await redis_monitor_task
            except asyncio.CancelledError:
                print(f"[{datetime.datetime.now()}] Redis monitoring task cancelled successfully")
            except Exception as e:
                print(f"[{datetime.datetime.now()}] Error during task cancellation: {str(e)}")
                
        print(f"[{datetime.datetime.now()}] Shutdown complete")

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        print(f"[{datetime.datetime.now()}] Global exception handler caught: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error occurred"}
        )
    
    print("Including application routers")
    app.include_router(task_router.router)
    app.include_router(ws_router.router)
    app.include_router(analytics_router.router)
    return app

app = get_application()