# ${{ values.name }}

${{ values.description }}

Django 5.2 LTS + Django REST Framework service on PostgreSQL (CloudNativePG in the cluster). Created from the Backstage template **New Django service**; full docs are in the **Docs** tab (`docs/`).

## Quick start

```sh
docker compose up -d --wait   # PostgreSQL on 127.0.0.1:5432
make install migrate run      # http://localhost:8000/api/items, /admin/
```

Quality gates (same as CI): `make lint typecheck test check`.

## Layout

```
src/config/        settings (base/dev/test/prod), urls, wsgi/asgi
src/core/          JSON logging, request-id middleware, health views
src/apps/items/    example app (model, admin, serializer, viewset, migration)
tests/             pytest-django
charts/${{ values.name }}/   Helm chart: app, CNPG database, migration Job, PDB, HPA
```

## Pinned versions

| What | Version |
|---|---|
| Python image | `python:3.13.18-slim-trixie@sha256:1b5c0692836eae9b028cc352d7146872f36939aa1fb0de24d3ef6df307b956c9` |
| uv | 0.13.7 (`ghcr.io/astral-sh/uv@sha256:96f40d3904aad8d0bd010539001d36c8e2188b981e1334471a90c4a1d93bb490`) |
| Django / DRF | 5.2.19 / 3.18.3 |
| gunicorn / psycopg | 27.0.0 / 3.3.8 |
| django-environ / django-prometheus / whitenoise | 0.14.0 / 2.5.0 / 6.12.0 |
| ruff / mypy / pytest | 0.17.4 / 2.4.1 / 9.2.0 |
| Database image (CNPG) | `ghcr.io/cloudnative-pg/postgresql:17.7-standard-trixie@sha256:e079dae5253fa6ed26fc65fda06d515af764dbec392dd4b46b17ab11eebd8131` |
| Actions | checkout v7.0.1, setup-uv v10.3.3, setup-helm v5.1.0, setup-qemu v4.4.0, setup-buildx v4.4.1, login v4.8.0, build-push v7.4.0 |
| Helm / yq (CI) | v4.1.0 / v4.54.3 |
