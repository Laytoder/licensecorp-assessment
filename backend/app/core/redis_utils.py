import redis
import json
import datetime
from app.core.config import settings
from app.core.constants import AnalyticsCounters, PAGE_SIZE, MAX_TASK_TTL, MAX_REDIS_MEMORY
from app.repositories.task_repository import TaskRepository
from app.core.database import get_db
from fastapi import Depends
from sqlalchemy.orm import Session
import asyncio

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)

redis_client.config_set("maxmemory", MAX_REDIS_MEMORY)
redis_client.config_set("maxmemory-policy", "allkeys-lfu")

def cache_set_task(task_id: int, task_data: dict, expiry_date: datetime.datetime | None = None):
    key = f"task:{task_id}"
    serialized_data = json.dumps(task_data, default=lambda o: o.isoformat() if hasattr(o, "isoformat") else str(o))
    created_at = task_data.get("created_at", datetime.datetime.utcnow())
    if isinstance(created_at, str):
        created_at = datetime.datetime.fromisoformat(created_at)

    pipe = redis_client.pipeline()
    if expiry_date:
        calculated_ttl = (expiry_date - datetime.datetime.utcnow()).total_seconds()
        ttl = min(calculated_ttl, MAX_TASK_TTL) if calculated_ttl > 0 else 0
        if ttl > 0:
            pipe.set(key, serialized_data, ex=int(ttl))
        else:
            pipe.delete(key)
    else:
        pipe.set(key, serialized_data, ex=MAX_TASK_TTL)
    pipe.zadd("tasks_sorted", {task_id: created_at.timestamp()})
    pipe.execute()

def cache_delete_task(task_id: int):
    key = f"task:{task_id}"
    pipe = redis_client.pipeline()
    pipe.delete(key)
    pipe.zrem("tasks_sorted", task_id)
    pipe.execute()

def cache_get_tasks_page_with_missing(page: int) -> (list, dict, list):
    start = (page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE - 1
    task_id_bytes = redis_client.zrevrange("tasks_sorted", start, end)
    if not task_id_bytes:
        return ([], {}, [])
    
    ordered_ids = []
    pipe = redis_client.pipeline()
    for task_id in task_id_bytes:
        task_id_parsed = int(task_id.decode("utf-8"))
        ordered_ids.append(task_id_parsed)
        pipe.get(f"task:{task_id_parsed}")
    results = pipe.execute()

    cached_tasks = {}
    missing_ids = []
    for task_id, data in zip(ordered_ids, results):
        if data:
            cached_tasks[task_id] = json.loads(data)
        else:
            missing_ids.append(task_id)
    return (ordered_ids, cached_tasks, missing_ids)

def increment_counter(counter: AnalyticsCounters):
    redis_client.incr(f"counter:{counter.value}")

def get_counter(counter: AnalyticsCounters) -> int:
    value = redis_client.get(f"counter:{counter.value}")
    return int(value) if value else 0

def rebuild_sorted_set_index(db: Session = Depends(get_db)):
    tasks = TaskRepository.get_tasks_for_cache_index(db)

    pipe = redis_client.pipeline()
    for task in tasks:
        pipe.zadd("tasks_sorted", {task.id: task.created_at.timestamp()})
    pipe.execute()

async def monitor_redis():
    redis_was_down = False
    while True:
        try:
            if redis_client.ping():
                if redis_was_down:
                    rebuild_sorted_set_index()
                    redis_was_down = False
            else:
                redis_was_down = True
        except Exception as e:
            if not redis_was_down:
                print("Redis appears to be down:", e)
            redis_was_down = True
        await asyncio.sleep(5)