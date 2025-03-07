# LicenseCorp Assessment

## Project Demo (Click On Image)

<a href="https://youtu.be/tIQlwfO3al4?si=cYfVyvP56BrU1GMA">
  <img src="https://i.imgur.com/N8nSvJi.jpeg" alt="Project Demo Video" width="600">
</a>

## Overview

This project is a high-performance task management system designed to handle millions of tasks efficiently. It uses a modern stack with:
- Backend: FastAPI with SQLAlchemy and Redis caching
- Frontend: Next.js
- Database: PostgreSQL
- Caching: Redis

## Running with Docker Compose

The entire application can be run using Docker Compose, which will set up all necessary services.

### Build and Start
```bash
docker-compose up --build -d
```

### Stop and Remove Containers
```bash
docker-compose down -v
```

### Complete Rebuild
If you're experiencing issues or need a clean slate:
```bash
docker-compose down -v
docker system prune -a
docker-compose up --build -d
```

## Component Documentation

- [Backend Documentation](./backend/README.md)
- [Frontend Documentation](./frontend/README.md)
- [Scripts Documentation](./scripts/README.md)

## Testing with 1 Million Tasks

This system is optimized for handling large volumes of tasks. To test with 1 million tasks:

1. Navigate to the `scripts` directory
2. Follow the instructions in the [Scripts README](./scripts/README.md) to run the task creation script

## Caching Strategy

Our system uses a sophisticated caching strategy to efficiently handle millions of tasks:

### Granular Caching Approach

- **Paged Retrieval**: Tasks are fetched by pages rather than all at once
- **Ordered Retrieval**: Newer tasks are displayed at the top for better user experience

### Redis Sorted Task Index

- Maintains a lightweight index (~100MB) containing only task ID and creation timestamp
- Optimizes memory usage while preserving sort order
- Enables quick retrieval of task IDs by page number

### Granular Task Caching

- Individual task details are cached with TTL of max 1 hour
- Expiry dates are respected for time-sensitive tasks
- Uses LFU (Least Frequently Used) eviction policy to manage memory efficiently

### Cache Synchronization

- **Write-Through Caching**: Cache is updated immediately on create/update/delete operations
- **Partial Fetching**: If some tasks are missing from cache, only those are fetched from DB
- **Transparent to User**: The application automatically handles mixed cache/DB retrieval

### Future Improvements

- **Hybrid Approach**: Caching entire pages along with individual tasks
- **Warm Caching**: Pre-loading frequently accessed tasks on Redis startup
- **Usage Analytics**: Monitoring page and task access patterns to optimize caching strategy

This caching strategy offers excellent performance for the current scale while providing room for further optimization as usage patterns emerge. 