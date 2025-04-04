# Verse - Monorepo Project

This is a monorepo containing both the frontend and backend services for the Verse application.

## Project Structure

```
verse/
├── apps/
│   ├── frontend/ - React/TypeScript frontend using Vite
│   └── backend/ - FastAPI Python backend
├── docker-compose.yml - Docker configuration for all services
└── README.md - This file
```

## Prerequisites

To run this project, you need to have the following installed:

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/) (usually included with Docker Desktop)

## Running the Project

The entire application can be run with a single command using Docker Compose:

```bash
docker-compose up -d
```

This will:
1. Build and start the frontend application
2. Build and start the backend API
3. Start a PostgreSQL database

### Accessing the Services

Once all containers are running, you can access:

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs - Interactive Swagger UI to explore and test the API
- **PostgreSQL Database**: 
  - Host: localhost
  - Port: 5432
  - Username: postgres
  - Password: postgres
  - Database: verse

### Viewing Logs

To view logs from all services:

```bash
docker-compose logs
```

Or for a specific service:

```bash
docker-compose logs frontend
docker-compose logs backend
docker-compose logs db
```

### Stopping the Project

To stop all running containers:

```bash
docker-compose down
```

To stop and remove all data (including the database volume):

```bash
docker-compose down -v
```

## Development

### Rebuilding After Changes

If you make changes to the code, rebuild the containers:

```bash
docker-compose build
docker-compose up -d
```

## Troubleshooting

- If you encounter port conflicts, ensure ports 5173, 8000, and 5432 are not in use by other applications.
- Check logs for specific errors: `docker-compose logs [service_name]`
