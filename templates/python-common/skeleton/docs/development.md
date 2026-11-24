# Development

Requirements: [uv](https://docs.astral.sh/uv/) 0.13.7 and Docker.

```sh
docker compose up -d --wait   # local PostgreSQL on 127.0.0.1:5432
make install                  # uv sync --locked (creates .venv)
make migrate                  # apply database migrations
make run                      # dev server on http://localhost:8000
```

Quality gates (the same ones CI runs):

```sh
make lint        # ruff check + ruff format --check
make typecheck   # mypy --strict
make test        # pytest with a coverage gate
make check       # framework-specific checks
make fmt         # auto-fix lint and formatting
```

Install the git hooks once with `uvx pre-commit install`.

## Layout

{% if values.framework == 'django' -%}
```
src/config/            settings (base/dev/prod/test), urls, wsgi/asgi
src/core/              logging, request-id middleware, health views
src/apps/items/        example app: model, admin, serializer, viewset, migrations
tests/                 pytest-django tests
gunicorn.conf.py       production server settings
```
{%- else -%}
```
src/app/main.py        application factory (routers, middleware, lifespan)
src/app/core/          settings, logging, request-id middleware, metrics
src/app/db/            async engine/session, declarative base
src/app/api/routes/    HTTP routes (health, items)
src/app/models/        SQLAlchemy models
src/app/schemas/       Pydantic request/response models
src/app/repositories/  database access
src/app/services/      business logic
alembic/               migrations
tests/                 pytest + httpx tests
gunicorn.conf.py       production server settings (uvicorn workers)
```
{%- endif %}
