import redis
import json
import datetime
from app.core.config import settings
from app.core.constants import AnalyticsCounters

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)

def cache_set_task(task_id: int, task_data: dict, expiry_date: datetime.datetime | None = None):
    key = f"task:{task_id}"
    serialized_data = json.dumps(task_data, default=lambda o: o.isoformat() if hasattr(o, "isoformat") else str(o))
    created_at = task_data.get("created_at", datetime.datetime.utcnow())
    if isinstance(created_at, str):
        created_at = datetime.datetime.fromisoformat(created_at)

    pipe = redis_client.pipeline()
    if expiry_date:
        ttl = (expiry_date - datetime.datetime.utcnow()).total_seconds()
        if ttl > 0:
            pipe.set(key, serialized_data, ex=int(ttl))
        else:
            pipe.delete(key)
    else:
        pipe.set(key, serialized_data)
    pipe.zadd("tasks_sorted", {task_id: created_at.timestamp()})
    pipe.execute()

def cache_get_task(task_id: int) -> dict | None:
    key = f"task:{task_id}"
    data = redis_client.get(key)
    if data:
        return json.loads(data)
    return None

def cache_get_all_tasks() -> list:
    task_ids = redis_client.zrange("tasks_sorted", 0, -1)
    tasks = []
    if not task_ids:
        return tasks

    pipe = redis_client.pipeline()
    for task_id in task_ids:
        pipe.get(f"task:{task_id.decode('utf-8')}")
    results = pipe.execute()

    for data in results:
        if data:
            tasks.append(json.loads(data))
    return tasks

def cache_delete_task(task_id: int):
    key = f"task:{task_id}"
    pipe = redis_client.pipeline()
    pipe.delete(key)
    pipe.zrem("tasks_sorted", task_id)
    pipe.execute()

def increment_counter(counter: AnalyticsCounters):
    redis_client.incr(f"counter:{counter.value}")

def get_counter(counter: AnalyticsCounters) -> int:
    value = redis_client.get(f"counter:{counter.value}")
    return int(value) if value else 0