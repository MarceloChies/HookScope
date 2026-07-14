# HookScope

HookScope is a webhook inspection, forwarding, and retry API built with FastAPI.

It gives developers a unique endpoint for receiving webhook events, stores each delivery for inspection, forwards events to a configured destination, and records every forwarding attempt.

## Current features

- Create webhook endpoints with a generated token
- Receive JSON webhooks at `POST /hooks/{token}`
- Capture request method, payload, and headers
- Redact sensitive headers such as cookies and API keys before storage
- Inspect all deliveries or one delivery
- Forward a received payload to an optional destination URL
- Record forwarding status codes, response bodies, errors, and attempt numbers
- Inspect forwarding-attempt history for a delivery
- Run locally or with Docker Compose and PostgreSQL
- Exercise the API through FastAPI's interactive Swagger documentation

## Architecture

```text
Webhook sender
    |
    v
POST /hooks/{token}
    |
    +--> PostgreSQL: delivery, sanitized headers, payload
    |
    +--> Optional destination URL
             |
             v
        PostgreSQL: delivery attempt, status, response, or error
```

## Technology

- Python 3
- FastAPI
- SQLAlchemy
- PostgreSQL
- HTTPX
- Docker and Docker Compose
- Pytest

## API overview

| Method | Route | Purpose |
| --- | --- | --- |
| `POST` | `/endpoints` | Create a webhook endpoint and token |
| `POST` | `/hooks/{token}` | Receive and optionally forward a webhook |
| `GET` | `/deliveries` | List captured webhook deliveries |
| `GET` | `/deliveries/{delivery_id}` | Inspect one delivery |
| `GET` | `/deliveries/{delivery_id}/attempts` | View forwarding attempts |
| `GET` | `/health` | Check whether the API is running |
| `GET` | `/health/database` | Check database connectivity |

Interactive API documentation is available at `/docs`.

## Run locally

### 1. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 3. Configure environment variables

Copy `.env.example` to `.env` and set your local PostgreSQL connection:

```env
DATABASE_URL=postgresql+psycopg://postgres:YOUR_POSTGRES_PASSWORD@localhost:5432/webhooks
APP_SECRET=replace-with-a-random-secret
ENVIRONMENT=development
```

### 4. Start the API

```powershell
python -m uvicorn app.main:app --reload
```

Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

## Run with Docker

Docker Compose starts both FastAPI and PostgreSQL:

```powershell
docker compose up --build
```

Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

The Docker PostgreSQL database is available to pgAdmin at:

```text
Host: localhost
Port: 5433
Database: webhooks
Username: postgres
Password: postgres
```

## Example flow

### Create an endpoint

`POST /endpoints`

```json
{
  "name": "Payments receiver",
  "destination_url": "https://example.com/webhooks/payments"
}
```

The response includes a generated `token`.

### Send a webhook

`POST /hooks/{token}`

```json
{
  "event": "payment.completed",
  "amount": 49.99
}
```

HookScope stores the delivery, forwards it when a destination URL is configured, and creates a forwarding-attempt record.

## Tests

Tests are separated by purpose:

```text
tests/
├── unit/       # Small isolated logic tests
└── feature/    # FastAPI API-flow tests using temporary SQLite storage
```

Run all tests:

```powershell
python -m pytest -v
```

Run a group:

```powershell
python -m pytest tests/unit -v
python -m pytest tests/feature -v
```

## Security notes

- Sensitive request headers are redacted before persistence.
- Do not commit `.env`; use `.env.example` for required variable names.
- This MVP accepts configurable destination URLs. Production hardening should include authentication, rate limiting, HMAC signature support, and SSRF protections.

## Roadmap

- [ ] Manual retry endpoint: `POST /deliveries/{delivery_id}/retry`
- [ ] Automatic retries with exponential backoff
- [ ] Endpoint management: list, update, and delete
- [ ] Alembic database migrations
- [ ] Authentication and per-user endpoints
- [ ] Rate limiting and destination URL protection
- [ ] Webhook signature verification
- [ ] Dashboard, event replay, and payload contract-drift detection

## License

This project is currently intended as a learning and portfolio project.