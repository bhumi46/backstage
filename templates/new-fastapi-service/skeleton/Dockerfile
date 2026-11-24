# syntax=docker/dockerfile:1
# Multi-stage: build the virtualenv with uv, ship only the venv + code on a slim runtime (no compilers).

FROM ghcr.io/astral-sh/uv:0.13.7@sha256:96f40d3904aad8d0bd010539001d36c8e2188b981e1334471a90c4a1d93bb490 AS uv

FROM python:3.13.18-slim-trixie@sha256:1b5c0692836eae9b028cc352d7146872f36939aa1fb0de24d3ef6df307b956c9 AS build
COPY --from=uv /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/app/.venv
WORKDIR /app
# Dependencies first (cached until pyproject.toml/uv.lock change).
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv uv sync --locked --no-dev
COPY gunicorn.conf.py alembic.ini ./
COPY alembic ./alembic
COPY src ./src
RUN /app/.venv/bin/python -m compileall -q src alembic

FROM python:3.13.18-slim-trixie@sha256:1b5c0692836eae9b028cc352d7146872f36939aa1fb0de24d3ef6df307b956c9 AS runtime
RUN groupadd --system --gid 10001 app && \
    useradd --system --uid 10001 --gid app --no-create-home --shell /usr/sbin/nologin app
WORKDIR /app
COPY --from=build /app /app
ENV PATH=/app/.venv/bin:$PATH \
    PYTHONPATH=/app/src \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
USER 10001:10001
EXPOSE 8000
CMD ["gunicorn", "-c", "gunicorn.conf.py", "app.main:app"]
