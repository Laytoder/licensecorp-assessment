# LicenseCorp Assessment Backend

This is the FastAPI backend for the LicenseCorp Assessment, designed to handle millions of todos efficiently using Redis caching and PostgreSQL.

## Features

- RESTful API for todo management
- Redis caching for high performance
- PostgreSQL database for data persistence
- Real-time analytics using WebSockets
- Optimized for handling large volumes of data

## Local Setup

### Prerequisites

- Python 3.9+
- PostgreSQL
- Redis

### Installation

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

### Running the Backend

Start the FastAPI server using Uvicorn:

```bash
uvicorn app.main:app --reload --port 8002
```

The backend will be available at http://localhost:8002

## Deployment

See the main [README.md](../README.md) for Docker deployment instructions. 