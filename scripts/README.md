# LicenseCorp Assessment Scripts

This directory contains utility scripts for the LicenseCorp Assessment.

## Million Task Creator

The primary script here is `create_million_tasks.py`, which helps test the system's performance with a large volume of tasks.

### Purpose

This script allows you to trigger the creation of 1 million tasks on the backend, enabling:
- Performance testing
- Caching efficiency evaluation
- Load testing

### Prerequisites

- Python 3.6+
- Backend server running at http://localhost:8002

### Setup

1. Create and activate a virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

### Running the Script

To trigger the creation of 1 million tasks:

```bash
python create_million_tasks.py
```

The script makes a single POST request to the backend endpoint `http://localhost:8002/tasks/populate/1000000`, which initiates the batch creation process on the server side.

### Monitoring Progress

After running the script, you can monitor the task creation progress:

1. Through the frontend UI at http://localhost:3000
2. Via the backend API at http://localhost:8002/tasks/stats
3. By watching the analytics counters at http://localhost:8002/analytics/counters

### Notes

- The script itself completes quickly as it only initiates the process
- The actual task creation happens asynchronously on the backend
- Creating 1 million tasks may take several minutes depending on your server's performance 