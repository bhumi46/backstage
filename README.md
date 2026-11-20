# backstage

The developer portal of the Backstage IDP lab (see [PLAN.md](PLAN.md), step 4): software catalog, software templates ("New Go service", "New environment") and plugins for GitHub Actions, Kubernetes, Argo CD and TechDocs. Backstage never runs Terraform or kubectl; templates only create repos and open PRs.

Built with `@backstage/create-app` using the **new frontend system**.

## Run locally

```sh
cp .env.example .env      # fill in GITHUB_TOKEN, AUTH_GITHUB_CLIENT_ID/SECRET, POSTGRES_PASSWORD
scripts/cluster-tokens.sh # adds K8S_CLUSTER_URL, K8S_SA_TOKEN, ARGOCD_AUTH_TOKEN from platform-infra (re-run after recreating the cluster)
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
| `K8S_CLUSTER_URL` / `K8S_SA_TOKEN` | Kubernetes plugin: kind API + read-only ServiceAccount (`platform-infra` `modules/backstage-access`) |
| `ARGOCD_AUTH_TOKEN` | Argo CD plugin, sent by the backend proxy `/argocd/api`: read-only Argo CD account `backstage` |
| `BACKSTAGE_TEST_TOKEN` | optional; static token for local API checks via the gitignored `app-config.local.yaml` |

## Plugins (step 4b)

| Plugin | Shows (on a Component page) | Needs |
|---|---|---|
| GitHub Actions | **CI/CD** tab: workflow runs | `github.com/project-slug`; your GitHub sign-in |
| Kubernetes | **Kubernetes** tab: deployments/pods in every namespace | `backstage.io/kubernetes-id`; label of the same name on the objects |
| Argo CD (Roadie) | **Argo CD** tab/cards: sync + health per app | `argocd/app-selector`; proxy `/argocd/api` |
| TechDocs | **Docs** tab | `backstage.io/techdocs-ref: dir:.` + `mkdocs.yml`; built locally in Docker |

The kind cluster has no metrics-server, so `skipMetricsLookup: true` is set for it. **Use Chrome or Firefox:** on `http://localhost`, Backstage sets the TechDocs cookie as `Secure`, which Safari refuses, so Docs fails there with "TypeError: Load failed".

## Catalog

- `catalog/org.yaml`: Group `platform-team`, User `bhumi46`, System `idp-lab`.
- `catalog/locations.yaml`: the `catalog-info.yaml` of `platform-infra`, `gitops`, `users-svc`, `orders-svc` and this repo, read from GitHub `main`.

## Software templates

### New Go service (`templates/new-go-service`)

Create → **New Go service**. Parameters: name, description, owner, environments (`dev`/`staging`), and a GitOps token (Secret field).

1. `fetch:template` renders `skeleton/` (same layout, CI and chart as `orders-svc`/`users-svc`; neutral `/api/items`). Workflow files and Helm templates are copied without templating.
2. `publish:github` creates public `bhumi46/<name>` and stores the token as its `GITOPS_TOKEN` Actions secret.
3. `fetch:template` (once per env) renders `gitops-skeleton/` → `apps/<name>-<env>.yaml` and `envs/<env>/<name>/values.yaml` with `image.tag` = the repo's first commit.
4. `publish:github:pull-request` opens that PR in `bhumi46/gitops`.
5. `catalog:register` adds the new component.

Merge the gitops PR once the new repo's first CI run is green (image + chart published). Until then CI's dev bump is skipped on purpose, so it can't conflict with the PR.

New repos get branch protection that requires a PR but no approving review, so a solo owner can merge.

### New environment (`templates/new-environment`)

Create → **New environment**. Parameters: name (e.g. `qa`), owner, CPU/memory/max-pods quota, and the services to deploy (any catalog Component of type `service`).

1. `gitops:read-image-tags` reads each service's `image.tag` from `gitops` `envs/dev/<svc>/values.yaml`. This is a small **read-only** action in this repo (`packages/backend/src/modules/gitopsActions`), because no built-in action can read a file's contents.
2. `fetch:template` + `publish:github:pull-request` open a PR in `bhumi46/platform-infra` adding `envs/local/environments/<env>.yaml` (`owner`, `cpu`, `memory`, `max_pods`).
3. `fetch:template` (once per service) + `publish:github:pull-request` open a PR in `bhumi46/gitops` adding `apps/<svc>-<env>.yaml` and `envs/<env>/<svc>/values.yaml` (dev tag, 1 replica; `orders-svc` gets `USERS_SVC_URL` for the same namespace).

Then, in this order:
1. Merge the platform-infra PR and run `terraform apply` in `platform-infra/envs/local` (you run it; Backstage never runs Terraform). This creates the namespace, ResourceQuota and LimitRange.
2. Merge the gitops PR. Argo CD deploys the services into the new namespace.

Each environment is a namespace in the same kind cluster, managed by the same Argo CD.

## Run in the cluster (step 4e)

The same app also runs in the kind cluster, deployed like any other service:

- **CI** (`.github/workflows/ci.yml`): `tsc`, lint, tests, then `yarn build:backend` and a multi-arch image `ghcr.io/bhumi46/backstage:<sha>` from `packages/backend/Dockerfile`, plus the OCI chart `charts/backstage`. The `bump` job sets `image.tag` in gitops `platform/backstage/values.yaml` (needs the `GITOPS_TOKEN` Actions secret, like the services).
- **Argo CD** deploys gitops `apps/backstage.yaml` into the `backstage` namespace (created by platform-infra): the Backstage Deployment plus its own PostgreSQL StatefulSet (1Gi PVC).
- **Config:** `app-config.yaml` + `app-config.production.yaml`. In the pod, the catalog reads `catalog/` and `templates/` from GitHub `main`. The Kubernetes plugin uses the pod's own read-only ServiceAccount `backstage-reader`, and the Argo CD proxy calls `argocd-server.argocd.svc`. TechDocs builds with mkdocs inside the pod.
- **Secrets** are not in git. `scripts/cluster-secrets.sh` copies `GITHUB_TOKEN`, `AUTH_GITHUB_CLIENT_ID/SECRET`, `ARGOCD_AUTH_TOKEN`, `POSTGRES_USER/PASSWORD` and `BACKSTAGE_TEST_TOKEN` from `.env` into the Secret `backstage/backstage-secrets`, without printing them. Re-run it after changing `.env` or recreating the cluster, then restart the pod.

Open it on the same port as local dev, so the GitHub OAuth callback still matches (stop `yarn start` first):

```sh
kubectl -n backstage port-forward svc/backstage 7007:7007   # http://localhost:7007
```

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
| `@backstage-community/plugin-github-actions` | 1.6.0 |
| `@roadiehq/backstage-plugin-argo-cd` | 2.13.1 |
| `@backstage/plugin-kubernetes` / `-backend` | 0.12.24 / 0.21.12 (from create-app) |
| `@backstage/plugin-techdocs` / `-backend` | 1.19.0 / 2.4.0 (from create-app) |
| `@backstage/plugin-scaffolder-node` (custom action) | 0.13.8 |
| `@backstage/backend-plugin-api` (custom action) | 1.11.0 |
| `yaml` (custom action) | 2.9.1 |
| Image base `node:24-trixie-slim` | `@sha256:af02d57b57719b9657a45199a79264a9437940cd55b3c7b3fc99615654f124a0` |
| `mkdocs-techdocs-core` (in the image) | 1.7.1 |
| Chart `charts/backstage` | 0.1.0 |
| `actions/setup-node` / `docker/setup-qemu-action` | v7.1.0 / v4.4.0 (other actions as in the services) |
| Helm / yq in CI | v4.1.0 / v4.54.3 |
| PostgreSQL image | `postgres:17.7-alpine@sha256:bb377b7239d2774ac8cc76f481596ce96c5a6b5e9d141f6d0a0ee371a6e7c0f2` |
