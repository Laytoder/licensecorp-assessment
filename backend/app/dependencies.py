from fastapi import Request, HTTPException, status
from app.core.redis_clients import redis_client
import time

# 100 requests per min per ip
def rate_limit(request: Request):
    client_ip = request.client.host
    key = f"rate:{client_ip}"
    limit = 100
    window = 60
    current = redis_client.incr(key)
    if current == 1:
        redis_client.expire(key, window)
    if current > limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too Many Requests"
        )