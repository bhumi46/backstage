# SKILLS.md

Repeatable playbooks for agents working in this repo. Each one says when to use it, the steps, and how to check it worked. Shared rules are in [AGENTS.md](AGENTS.md); the full lab plan is in [PLAN.md](PLAN.md).

---

## 1. Bootstrap the Backstage app (plan 4a)

**Use when:** the repo has no Backstage app yet.

1. `npx @backstage/create-app@<pinned>` into this directory; record the version in `README.md`.
2. Add `docker-compose.yaml` with PostgreSQL; set `backend.database.client: pg` with `POSTGRES_*` env vars.
3. Configure `integrations.github` with `${GITHUB_TOKEN}`.
4. Add GitHub auth provider + sign-in resolver (`usernameMatchingUserEntityName`).
5. Add `catalog/org.yaml` (Group `platform-team`, Users) and register the 5 repos' `catalog-info.yaml` (or GitHub discovery for `<owner>`).

**Check:** `yarn start` works, sign-in works, catalog lists all components with owners and the `orders-svc → users-svc` dependency.

---

## 2. Add a plugin (plan 4b)

**Use when:** adding GitHub Actions, Kubernetes, Argo CD or TechDocs.

1. Install pinned frontend + backend packages with `yarn --cwd packages/app add` / `yarn --cwd packages/backend add`.
2. Register the backend module in `packages/backend/src/index.ts`.
3. Add the entity card/tab in `packages/app/src/components/catalog/EntityPage.tsx`.
4. Add config to `app-config.yaml` using env vars for tokens:
   - Kubernetes: kind cluster URL + ServiceAccount token (`K8S_SA_TOKEN`), `skipTLSVerify: true` for local only.
   - Argo CD: `http://localhost:8080` + `ARGOCD_AUTH_TOKEN`.
5. Record the versions in `README.md`.

**Check:** `yarn tsc` passes; the tab shows data on the `orders-svc` page.

---

## 3. Write or change a software template (plan 4c / 4d)

**Use when:** editing `templates/new-go-service` or `templates/new-environment`.

1. Skeleton files use `${{ values.<param> }}`; keep paths identical to the target repos (see AGENTS.md).
2. Only use `fetch:template`, `publish:github`, `publish:github:pull-request`, `catalog:register`. No cluster/infra mutation.
3. Always add `output.links` for the repo, PR(s) and catalog entity.
4. Register the template in `app-config.yaml` under `catalog.locations` with `rules: [{allow: [Template]}]`.

**Check:** use the dry-run in **Create → Template Editor**, then a real run (e.g. `payments-svc`, env `qa`) and confirm the PRs match the existing `gitops`/`platform-infra` layout.

---

## 4. Build and deploy Backstage to the cluster (plan 4e, optional)

1. `yarn build:backend`, then `docker build -f packages/backend/Dockerfile -t ghcr.io/<owner>/backstage:<sha> .`
2. Push to GHCR; add a Helm chart and `apps/backstage.yaml` in `gitops`.

**Check:** the Argo CD app `backstage` is Synced/Healthy and the UI loads through the cluster.

---

## 5. Verify a step is done

1. Re-read the step's **Done when** list in `PLAN.md`.
2. Run `yarn tsc && yarn lint:all && yarn test:all`.
3. Tick each box with evidence (command output, URL, screenshot). Report anything that didn't pass; don't move on.
4. Commit with a message naming the plan step (e.g. `step 4b: add argo cd plugin`).
