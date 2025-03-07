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

3. Set up environment variables (create a `.env` file in the backend directory):

```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/taskdb
REDIS_URL=redis://localhost:6379/0
```

### Running the Backend

Start the FastAPI server using Uvicorn:

```bash
uvicorn app.main:app --reload --port 8002
```

The backend will be available at http://localhost:8002

### API Documentation

Once the server is running, you can access:

- Swagger documentation: http://localhost:8002/docs
- ReDoc documentation: http://localhost:8002/redoc

## Testing

Run tests using pytest:

```bash
pytest
```

## Deployment

See the main [README.md](../README.md) for Docker deployment instructions. 