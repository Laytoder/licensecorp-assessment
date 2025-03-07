import asyncio
import redis
from threading import Thread
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.config import settings

router = APIRouter(prefix="/ws", tags=["WebSocket"])

# sub redis client
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)

@router.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    pubsub = redis_client.pubsub()
    thread = None

    try:
        pubsub.subscribe(settings.TASKS_CHANNEL)

        def redis_listener():
            try:
                for message in pubsub.listen():
                    if message["type"] == "message":
                        data = message["data"]
                        try:
                            asyncio.run(websocket.send_text(data.decode("utf-8")))
                        except (RuntimeError, asyncio.CancelledError):
                            # Connection closed or event loop issues
                            break
            except:
                # Any error in the listener should break the loop
                pass

        thread = Thread(target=redis_listener, daemon=True)
        thread.start()

        while True:
            try:
                await websocket.receive_text()
            except:
                # Any error should break the connection
                break

    finally:
        # Clean up resources
        try:
            pubsub.unsubscribe()
            pubsub.close()
        except:
            pass
        
        if thread:
            thread.join(timeout=1.0)  # Wait up to 1 second for thread to finish
        
        try:
            await websocket.close()
        except:
            pass