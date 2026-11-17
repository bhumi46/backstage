# backstage

The developer portal of the Backstage IDP lab (see [PLAN.md](PLAN.md), step 4): software catalog, software templates ("New Go service", "New environment") and plugins for GitHub Actions, Kubernetes, Argo CD and TechDocs. Backstage never runs Terraform or kubectl; templates only create repos and open PRs.

Built with `@backstage/create-app` using the **new frontend system**.

## Run locally

```sh
cp .env.example .env      # fill in GITHUB_TOKEN, AUTH_GITHUB_CLIENT_ID/SECRET, POSTGRES_PASSWORD
corepack enable
yarn install
scripts/start.sh          # loads .env, starts PostgreSQL (docker compose), runs yarn start
```

Frontend http://localhost:3000, backend http://localhost:7007. Sign in with GitHub; the login must match a `User` in `catalog/org.yaml`.

### Secrets (`.env`, gitignored)

| Variable | Used for |
|---|---|
| `GITHUB_TOKEN` | `integrations.github`: read catalog files, create repos, open PRs |
| `AUTH_GITHUB_CLIENT_ID` / `AUTH_GITHUB_CLIENT_SECRET` | GitHub OAuth app (callback `http://localhost:7007/api/auth/github/handler/frame`) |
| `POSTGRES_HOST` / `POSTGRES_PORT` / `POSTGRES_USER` / `POSTGRES_PASSWORD` | local PostgreSQL |

## Catalog

- `catalog/org.yaml`: Group `platform-team`, User `bhumi46`, System `idp-lab`.
- `catalog/locations.yaml`: the `catalog-info.yaml` of `platform-infra`, `gitops`, `users-svc`, `orders-svc` and this repo, read from GitHub `main`.

## Checks

```sh
yarn tsc && yarn lint:all && yarn test:all
```

## Pinned versions

Backstage packages use the ranges written by create-app; `yarn.lock` pins the exact versions.

| What | Version |
|---|---|
| Backstage release (`backstage.json`) | 1.56.0 |
| `@backstage/create-app` | 0.9.3 (new frontend system) |
| Yarn | 4.13.0 (`packageManager`) |
| Node.js | 22 (local 22.23.5; `engines: 22 \|\| 24`) |
| `@backstage/plugin-auth-backend-module-github-provider` | 0.5.8 |
| `@backstage/frontend-defaults` | 0.5.7 |
| `@backstage/plugin-catalog-backend` | 4.0.2 |
| PostgreSQL image | `postgres:17.7-alpine@sha256:bb377b7239d2774ac8cc76f481596ce96c5a6b5e9d141f6d0a0ee371a6e7c0f2` |
