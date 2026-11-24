# Same targets in every Python service; CI runs: install lint typecheck test check.
.PHONY: install lint fmt typecheck test check run migrate

install:
	uv sync --locked

lint:
	uv run ruff check .
	uv run ruff format --check .

fmt:
	uv run ruff check --fix .
	uv run ruff format .

typecheck:
	uv run mypy

test:
	uv run pytest

# Migrations apply cleanly from scratch and the models match them (no pending autogenerate).
check:
	uv run alembic upgrade head
	uv run alembic check

run:
	PYTHONPATH=src uv run uvicorn app.main:app --reload --port 8000

migrate:
	uv run alembic upgrade head
