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

# Production settings sanity check + no model change without a migration.
check:
	DJANGO_SETTINGS_MODULE=config.settings.prod DJANGO_SECRET_KEY=$$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))') \
		uv run python manage.py check --deploy --fail-level ERROR
	uv run python manage.py makemigrations --check --dry-run

run:
	uv run python manage.py runserver 0.0.0.0:8000

migrate:
	uv run python manage.py migrate
