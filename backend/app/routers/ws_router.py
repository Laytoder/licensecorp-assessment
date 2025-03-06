import asyncio
import redis
from threading import Thread
from fastapi import APIRouter, WebSocket
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
    pubsub.subscribe(settings.TASKS_CHANNEL)

    def redis_listener():
        for message in pubsub.listen():
            if message["type"] == "message":
                data = message["data"]
                asyncio.run(websocket.send_text(data.decode("utf-8")))

    thread = Thread(target=redis_listener, daemon=True)
    thread.start()

    try:
        while True:
            _ = await websocket.receive_text()
    except:
        pubsub.close()
        thread.join()