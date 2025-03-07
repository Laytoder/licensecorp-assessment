import asyncio
from threading import Thread
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.config import settings
from app.core.redis_clients import create_pubsub

router = APIRouter(prefix="/ws", tags=["WebSocket"])

@router.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    pubsub = create_pubsub()
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