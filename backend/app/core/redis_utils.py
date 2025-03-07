import json
import datetime
from app.core.config import settings
from app.core.constants import AnalyticsCounters, PAGE_SIZE, MAX_TASK_TTL, MAX_REDIS_MEMORY
from app.repositories.task_repository import TaskRepository
from app.core.database import get_db
from sqlalchemy.orm import Session
import asyncio
from app.core.redis_clients import redis_client, pubsub_redis

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
    # Check if the sorted set exists in Redis
    if not redis_client.exists("tasks_sorted"):
        print(f"[{datetime.datetime.now()}] tasks_sorted index not found in Redis, rebuilding it...")
        try:
            # Use the function's internal session handling
            rebuild_sorted_set_index()
        except Exception as e:
            print(f"[{datetime.datetime.now()}] Error rebuilding tasks_sorted index: {str(e)}")
    
    # Continue with original functionality
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
    new_value = redis_client.incr(f"counter:{counter.value}")
    
    counter_event = {
        "event": "counter_updated",
        "counter": counter.value,
        "value": new_value,
        "timestamp": datetime.datetime.utcnow().isoformat()
    }
    
    pubsub_redis.publish(
        settings.TASKS_CHANNEL,
        json.dumps(counter_event)
    )

def get_counter(counter: AnalyticsCounters) -> int:
    value = redis_client.get(f"counter:{counter.value}")
    return int(value) if value else 0

def rebuild_sorted_set_index(db=None):
    print(f"[{datetime.datetime.now()}] Rebuilding tasks_sorted index...")
    
    # Create a session if one wasn't provided
    session_created = False
    if db is None:
        from app.core.database import SessionLocal
        db = SessionLocal()
        session_created = True
    
    try:
        tasks = TaskRepository.get_tasks_for_cache_index(db)
        
        if not tasks:
            print(f"[{datetime.datetime.now()}] No tasks found to rebuild index")
            return
            
        print(f"[{datetime.datetime.now()}] Rebuilding index with {len(tasks)} tasks")
        pipe = redis_client.pipeline()
        for task in tasks:
            pipe.zadd("tasks_sorted", {task.id: task.created_at.timestamp()})
        pipe.execute()
        print(f"[{datetime.datetime.now()}] Successfully rebuilt tasks_sorted index")
    finally:
        # Only close the session if we created it
        if session_created:
            db.close()

async def monitor_redis():
    redis_was_down = False
    while True:
        print("monitoring redis")
        try:
            if redis_client.ping():
                if redis_was_down:
                    # Let rebuild_sorted_set_index handle its own session
                    rebuild_sorted_set_index()
                    redis_was_down = False
            else:
                redis_was_down = True
        except Exception as e:
            if not redis_was_down:
                print("Redis appears to be down:", e)
            redis_was_down = True
        await asyncio.sleep(5)