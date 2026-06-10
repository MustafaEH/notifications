# Notifications Service

A FastAPI-based notification API with JWT authentication, Redis caching, rate limiting, and asynchronous processing via Celery.

## Stack

- **API** — FastAPI + Uvicorn
- **Database** — PostgreSQL (SQLAlchemy)
- **Cache & broker** — Redis
- **Workers** — Celery

## Quick start (Docker)

**Prerequisites:** Docker and Docker Compose

```bash
docker compose up -d
```

| Service | URL / port |
|---------|------------|
| API | http://localhost:8000 |
| API docs | http://localhost:8000/docs |
| PostgreSQL | `localhost:5432` |
| Redis | `localhost:6379` |

Stop the stack:

```bash
docker compose down
```

## API overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/register` | Create a user account |
| `POST` | `/auth/login` | Login with email and password |
| `POST` | `/auth/token` | OAuth2 token endpoint (for Swagger) |
| `GET` | `/auth/me` | Current user profile (auth required) |
| `POST` | `/notifications/` | Create a notification (auth required) |
| `GET` | `/notifications/` | List your notifications (auth required) |
| `GET` | `/notifications/{id}` | Get a notification by ID (auth required) |
| `DELETE` | `/notifications/{id}` | Delete a notification (auth required) |

Creating a notification enqueues a Celery task that processes it asynchronously (`pending` → `processing` → `successful` or `dead`).

## Example flow

```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","username":"user1","full_name":"User One","password":"secret123"}'

# Get a token
curl -X POST http://localhost:8000/auth/token \
  -d "username=user@example.com&password=secret123"

# Create a notification
curl -X POST http://localhost:8000/notifications/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"recipient":"alice@example.com","channel":"email","subject":"Hello","content":"Test message"}'
```

## Environment variables

Docker Compose sets these automatically. For local development, copy and adjust as needed:

| Variable | Description | Default (Docker) |
|----------|-------------|------------------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@db:5432/notifications` |
| `REDIS_HOST` | Redis hostname | `redis` |
| `REDIS_URL` | Redis URL for Celery | `redis://redis:6379/0` |
| `JWT_SECRET` | Signing key for JWT tokens | — |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTE` | Token lifetime in minutes | `30` |

## Local development (without Docker)

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

pip install -r requirements.txt
```

Ensure PostgreSQL and Redis are running locally, then set a `.env` file with your connection details and start the services:

```bash
uvicorn main:app --reload
celery -A services.celery_app.celery_app worker --loglevel=info
```

## Tests

```bash
pytest
```

## Project structure

```
├── main.py                 # FastAPI app entry point
├── database.py             # SQLAlchemy engine and session
├── tasks.py                # Celery notification processing task
├── auth/                   # JWT and password utilities
├── models/                 # SQLAlchemy models
├── routers/                # API route handlers
├── schemas/                # Pydantic request/response models
├── services/               # Redis, Celery, rate limiting
├── tests/                  # Pytest suite
├── Dockerfile
└── docker-compose.yml
```
