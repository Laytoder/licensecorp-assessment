import requests
import concurrent.futures
import time
from ratelimit import limits, sleep_and_retry

BASE_URL = "http://localhost:8002/tasks/"
NUM_TASKS = 1_000_000  # one million tasks
CALLS = 100           # maximum of 100 requests
PERIOD = 60           # per 60 seconds (1 minute)

# Decorate the create_task function to enforce the rate limit.
@sleep_and_retry
@limits(calls=CALLS, period=PERIOD)
def create_task(task_num: int):
    payload = {
        "title": f"Task {task_num}",
        "description": f"Description for task {task_num}",
        "completed": False
        # Optionally add an expiry_date if needed, e.g. "expiry_date": "2025-12-31T23:59:59"
    }
    try:
        response = requests.post(BASE_URL, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Task {task_num} failed: {e}")
        return None

def main():
    start_time = time.time()
    completed = 0

    # Use a ThreadPoolExecutor with a limited number of workers.
    # Note: The rate limiter will ensure that overall we do not exceed 100 requests per minute.
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # Submit tasks for execution
        futures = {executor.submit(create_task, i): i for i in range(1, NUM_TASKS + 1)}
        for future in concurrent.futures.as_completed(futures):
            task_num = futures[future]
            result = future.result()
            if result is not None:
                completed += 1
            # Optionally print progress every 100 tasks
            if task_num % 100 == 0:
                print(f"Processed task {task_num}. Total completed: {completed}")
    
    end_time = time.time()
    print(f"Created {completed} tasks in {end_time - start_time:.2f} seconds.")

if __name__ == "__main__":
    main()
