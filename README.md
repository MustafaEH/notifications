# Notifications API

A backend service for creating and managing notifications asynchronously. Built as a hands-on project to practice core backend concepts — REST API design, authentication, background jobs, caching, and containerized deployment.

## Highlights

- **JWT authentication** with password hashing and protected routes
- **Async processing** — notifications are queued and processed by Celery workers
- **Redis** for caching list responses and per-user rate limiting (60 req/min)
- **Retry logic** with exponential backoff; failed deliveries move to a dead state after max retries
- **Docker Compose** stack: API, Celery worker, PostgreSQL, and Redis
- **Automated tests** with pytest and load testing with Locust

## Tech Stack

| Layer | Technology |
|-------|------------|
| API | FastAPI, Uvicorn |
| Database | PostgreSQL, SQLAlchemy |
| Cache / Message broker | Redis |
| Background tasks | Celery |
| Auth | JWT (Bearer tokens), Passlib |
| Testing | pytest, Locust |
| Deployment | Docker, Docker Compose |

## Architecture

```
Client
  │
  ▼
FastAPI (API) ──────► PostgreSQL
  │                        ▲
  ├── Redis (cache, rate limit)
  │
  └── enqueue task ──► Redis (broker)
                              │
                              ▼
                        Celery Worker ──► PostgreSQL
```

**Notification lifecycle:** `pending` → `processing` → `successful` or `dead` (after retries)

## Quick Start

**Prerequisites:** [Docker](https://docs.docker.com/get-docker/) and Docker Compose

```bash
git clone https://github.com/MustafaEH/notifications.git
cd notifications
docker compose up -d
```

| Service | URL |
|---------|-----|
| API | http://localhost:8000 |
| Interactive docs | http://localhost:8000/docs |

Stop the stack:

```bash
docker compose down
```

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/auth/register` | — | Register a new user |
| `POST` | `/auth/login` | — | Login and receive a JWT |
| `GET` | `/auth/me` | ✓ | Get current user profile |
| `POST` | `/notifications/` | ✓ | Create a notification (queued for processing) |
| `GET` | `/notifications/` | ✓ | List your notifications |
| `GET` | `/notifications/{id}` | ✓ | Get a single notification |
| `DELETE` | `/notifications/{id}` | ✓ | Delete a notification |

## Example Usage

```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","username":"user1","full_name":"User One","password":"secret123"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"secret123"}'

# Create a notification
curl -X POST http://localhost:8000/notifications/ \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{"recipient":"alice@example.com","channel":"email","subject":"Hello","content":"Test message"}'
```

## Local Development

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

pip install -r requirements.txt
```

Create a `.env` file with your local database and Redis settings, then run:

```bash
uvicorn main:app --reload
celery -A services.celery_app.celery_app worker --loglevel=info
```

## Testing

```bash
pytest
```

Load testing (requires the API to be running):

```bash
locust -f locustfile.py --host http://localhost:8000
```

## Project Structure

```
├── main.py              # Application entry point
├── database.py          # Database engine and session
├── tasks.py             # Celery background tasks
├── auth/                # JWT and password utilities
├── models/              # SQLAlchemy ORM models
├── routers/             # API route handlers
├── schemas/             # Pydantic request/response models
├── services/            # Redis, Celery, rate limiting
├── tests/               # pytest test suite
├── Dockerfile
└── docker-compose.yml
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_HOST` | Redis hostname (used by cache client) |
| `REDIS_URL` | Redis URL for Celery broker/backend |
| `JWT_SECRET` | Secret key for signing JWTs |
| `JWT_ALGORITHM` | JWT signing algorithm (default: `HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTE` | Token expiry in minutes |

Docker Compose sets all of these automatically for the containerized stack.
