# Weather Proxy Backend

FastAPI service that proxies Open-Meteo with Redis caching, MongoDB persistence,
retry plus circuit-breaker resilience, and structured logging.

See the [root README](../README.md) for full setup, architecture, and run
instructions. This service is normally started via the root `docker compose up`.

## Quick local run (without Docker)

```bash
uv sync
uv run uvicorn app.main:app --reload
```

Open API docs at http://localhost:8000/docs.
