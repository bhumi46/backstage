# ${{ values.name }}

${{ values.description }}

{% if values.framework == 'django' -%}
A **Django 5.2 LTS** service with Django REST Framework and the Django admin, backed by PostgreSQL.
{%- else -%}
A **FastAPI** service with async SQLAlchemy 2 and Alembic migrations, backed by PostgreSQL.
{%- endif %}

Created from the Backstage template *New {% if values.framework == 'django' %}Django{% else %}FastAPI{% endif %} service*.

## Endpoints

| Path | Purpose |
|---|---|
| `GET /healthz` | Liveness: the process is up |
| `GET /readyz` | Readiness: the database answers `SELECT 1` |
| `GET /metrics` | Prometheus metrics |
| `/api/items` | Example resource (list, create, get) |
{%- if values.framework == 'django' %}
| `/admin/` | Django admin |
{%- else %}
| `/docs` | OpenAPI UI |
{%- endif %}
{%- if values.dependsOn %}

## Dependencies

Calls `${{ values.dependsOn | parseEntityRef | pick('name') }}` at the URL in `${{ values.dependsOn | parseEntityRef | pick('name') | upper | replace('-', '_') }}_URL`.
{%- endif %}
