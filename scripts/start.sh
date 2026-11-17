#!/usr/bin/env bash
# Load .env, start PostgreSQL, then run Backstage (frontend :3000, backend :7007).
set -euo pipefail
cd "$(dirname "$0")/.."
[ -f .env ] || { echo "missing .env: cp .env.example .env and fill it in" >&2; exit 1; }
set -a; . ./.env; set +a
for v in GITHUB_TOKEN AUTH_GITHUB_CLIENT_ID AUTH_GITHUB_CLIENT_SECRET POSTGRES_PASSWORD; do
  [ -n "${!v:-}" ] || { echo "$v is empty in .env" >&2; exit 1; }
done
docker compose up -d --wait
exec yarn start "$@"
