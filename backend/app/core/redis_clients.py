import redis
from app.core.config import settings
from app.core.constants import MAX_REDIS_MEMORY

# Main Redis client for general operations and caching
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)

# Configure memory settings for the main client
redis_client.config_set("maxmemory", MAX_REDIS_MEMORY)
redis_client.config_set("maxmemory-policy", "allkeys-lfu")

# Publisher client for task events
pubsub_redis = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)

# WebSocket subscriber client
ws_redis = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)

# Function to create a new pubsub object from the ws_redis client
def create_pubsub():
    return ws_redis.pubsub() 