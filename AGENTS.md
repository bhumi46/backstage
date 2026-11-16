# AGENTS.md

Instructions for any AI coding agent (Claude Code, Codex, Cursor, etc.) working in this repo.

## What this repo is

`backstage` is one of five repos in the **Backstage IDP lab** (full plan: [PLAN.md](PLAN.md)). It holds:

- The Backstage app (created with `npx @backstage/create-app@latest`)
- Software templates: **New Go service** and **New environment**
- Optionally, the Helm chart / image for running Backstage in the kind cluster (step 4e)

Sibling repos (separate GitHub repos, all under `<owner>`):

| Repo | Role |
|---|---|
| `platform-infra` | Terraform: kind cluster, namespaces/quotas, Argo CD bootstrap |
| `gitops` | Argo CD Applications + per-env Helm values (desired state) |
| `orders-svc` | Go service; depends on `users-svc` |
| `users-svc` | Go service |
| `backstage` | **this repo** |

## Core rule

**Backstage never runs Terraform or kubectl.** Templates only create repos and open PRs (`publish:github`, `publish:github:pull-request`). Terraform and Argo CD apply the changes. Don't add scaffolder actions that mutate the cluster or infra directly.

## Expected layout

```
packages/app/                 frontend (plugins: GitHub Actions, Kubernetes, Argo CD, TechDocs)
packages/backend/             backend (catalog, scaffolder, auth, kubernetes, techdocs)
templates/
  new-go-service/template.yaml + skeleton/   (copied from orders-svc, ${{ values.name }} placeholders)
  new-environment/template.yaml + skeleton/  (env YAML for platform-infra, values for gitops)
catalog/                      org.yaml (Group platform-team, Users), locations
app-config.yaml               base config; secrets via env vars only
app-config.local.yaml         local overrides (gitignored)
docker-compose.yaml           local PostgreSQL
```

## Commands

```sh
corepack enable
yarn install
docker compose up -d          # PostgreSQL
yarn start                    # http://localhost:3000 (backend :7007)
yarn tsc                      # type check
yarn lint:all
yarn test:all
yarn build:backend            # before building packages/backend/Dockerfile
```

## Conventions

- Replace `<owner>` with the real GitHub user/org; never hard-code a different one.
- **Pin every version** (npm packages, plugins, images, charts, actions) and record it in `README.md`.
- **Secrets only via env vars** (`GITHUB_TOKEN`, `AUTH_GITHUB_CLIENT_ID/SECRET`, `ARGOCD_AUTH_TOKEN`, `K8S_SA_TOKEN`, `POSTGRES_*`). Never commit tokens; keep `app-config.local.yaml` gitignored.
- Catalog annotations a service must carry so plugins work:
  ```yaml
  github.com/project-slug: <owner>/<svc>
  backstage.io/kubernetes-id: <svc>
  argocd/app-selector: app.kubernetes.io/name=<svc>
  backstage.io/techdocs-ref: dir:.
  ```
- Template output paths must match the other repos exactly:
  - gitops: `apps/<name>-<env>.yaml`, `envs/<env>/<name>/values.yaml`
  - platform-infra: `envs/local/environments/<env>.yaml` (fields: `owner`, `cpu`, `memory`, `max_pods`)
- Generated Argo CD Applications: multi-source (chart + `$values` ref), destination namespace = env, `syncPolicy.automated` with prune + selfHeal, label `app.kubernetes.io/name=<svc>`.
- Work one plan step at a time; finish its **Done when** checklist before moving on. Commit after each sub-step with a clear message.
