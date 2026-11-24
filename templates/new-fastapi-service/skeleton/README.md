# ${{ values.name }}

${{ values.description }}

FastAPI service with async SQLAlchemy 2 and Alembic on PostgreSQL (CloudNativePG in the cluster). Created from the Backstage template **New FastAPI service**; full docs are in the **Docs** tab (`docs/`).

## Quick start

```sh
docker compose up -d --wait   # PostgreSQL on 127.0.0.1:5432
make install migrate run      # http://localhost:8000/docs
```

Quality gates (same as CI): `make lint typecheck test check`.

New migration after changing a model: `uv run alembic revision --autogenerate -m "describe change"`.

## Layout

```
src/app/main.py         application factory (lifespan, middleware, routers)
src/app/core/           settings, JSON logging, request-id + metrics middleware
src/app/db/             async engine/session, declarative base
src/app/api/            dependencies and routes (health, items)
src/app/models/         SQLAlchemy models
src/app/schemas/        Pydantic request/response models
src/app/repositories/   database access
src/app/services/       business logic
alembic/                migrations
tests/                  pytest + httpx against a real PostgreSQL
charts/${{ values.name }}/   Helm chart: app, CNPG database, migration Job, PDB, HPA
```

## Pinned versions

| What | Version |
|---|---|
| Python image | `python:3.13.18-slim-trixie@sha256:1b5c0692836eae9b028cc352d7146872f36939aa1fb0de24d3ef6df307b956c9` |
| uv | 0.13.7 (`ghcr.io/astral-sh/uv@sha256:96f40d3904aad8d0bd010539001d36c8e2188b981e1334471a90c4a1d93bb490`) |
| FastAPI / pydantic / pydantic-settings | 0.162.4 / 2.14.3 / 2.16.2 |
| SQLAlchemy / Alembic / psycopg | 2.1.8 / 1.20.1 / 3.3.8 |
| gunicorn / uvicorn / uvicorn-worker | 27.0.0 / 0.54.0 / 0.4.0 |
| httpx / prometheus-client | 0.28.1 / 0.26.0 |
| ruff / mypy / pytest | 0.17.4 / 2.4.1 / 9.2.0 |
| Database image (CNPG) | `ghcr.io/cloudnative-pg/postgresql:17.7-standard-trixie@sha256:e079dae5253fa6ed26fc65fda06d515af764dbec392dd4b46b17ab11eebd8131` |
| Actions | checkout v7.0.1, setup-uv v10.3.3, setup-helm v5.1.0, setup-qemu v4.4.0, setup-buildx v4.4.1, login v4.8.0, build-push v7.4.0 |
| Helm / yq (CI) | v4.1.0 / v4.54.3 |

Dependencies resolve with `exclude-newer = 2026-11-11` (in `pyproject.toml`), so nothing newer than the pins sneaks in through transitive dependencies.
