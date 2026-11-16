# Backstage IDP lab: plan

A hands-on lab for learning how an internal developer portal (IDP) built on **Backstage** provisions services and environments. Everything runs on a local **kind** cluster.

| Concern | Tool |
|---|---|
| Infrastructure | Terraform (kind cluster, namespaces, Argo CD) |
| CI | GitHub Actions (test, build, push to GHCR, bump image tag) |
| Packaging | Helm |
| CD | Argo CD (GitOps, app-of-apps) |
| Portal | Backstage (catalog, templates, plugins) |

Architecture diagram: `idp-plan/idp-lab-architecture.png` (Mermaid source in `idp-lab-architecture.mmd`).

---

## How to use this file with Claude Code

- Do **one step at a time**. Each step ends with a **Done when** checklist; don't move on until every box is ticked.
- Replace `<owner>` everywhere with your GitHub user or org.
- Pin every version you install (charts, images, actions, Go modules) and write it down in the repo README.
- Commit after each sub-step with a clear message.

---

## 0. Prerequisites and repos

**Tools on your machine:** Docker, kind, kubectl, Helm 3, Terraform ≥ 1.6, Go ≥ 1.22, Node.js LTS + Yarn (via `corepack enable`), the `gh` CLI, and optionally the `argocd` CLI.

**Create 5 GitHub repos (separate repos, which is the production model):**

| Repo | Contents |
|---|---|
| `platform-infra` | Terraform: kind cluster, environments, Argo CD bootstrap |
| `gitops` | Argo CD Applications + per-environment Helm values (the desired state) |
| `orders-svc` | Go service #1: code, Dockerfile, Helm chart, CI |
| `users-svc` | Go service #2: same layout |
| `backstage` | The Backstage app + software templates |

Why separate repos: infra, desired state and app code change at different speeds and need different access. Separating them also avoids CI loops, because CI commits image tags to `gitops`, not to the repo that triggered it.

**Secrets:**
- A GitHub PAT (or GitHub App) with `repo` + `workflow` scope, stored as the `GITOPS_TOKEN` secret in both service repos, so CI can push to `gitops`.
- Make GHCR packages public, or create an `imagePullSecret` in each namespace.

**Done when:** all tools print a version, all 5 repos exist, and the secret is set.

---

## 1. Infrastructure with Terraform (`platform-infra`)

**Goal:** `terraform apply` gives you a kind cluster with Argo CD, `dev` and `staging` namespaces, and a root app pointing at `gitops`.

**Layout:**
```
modules/
  kind-cluster/   tehcyx/kind provider; 1 control plane + 1 worker; map NodePort 30080 -> localhost:8080
  environments/   for_each env: Namespace + ResourceQuota + LimitRange (kubernetes provider)
  argocd/         helm_release argo-cd (server.insecure=true, NodePort 30080)
                  helm_release argocd-apps -> "root" Application: repo gitops, path apps/, recurse, automated prune+selfHeal
envs/local/
  main.tf         wires modules; configures helm + kubernetes providers from kind outputs
  environments/   dev.yaml, staging.yaml  (owner, cpu, memory, max_pods)
  outputs.tf      kubeconfig path, Argo CD URL, command to read the admin password
.github/workflows/terraform.yml
catalog-info.yaml (Resource: idp-lab-cluster, Component: platform-infra)
```

**Key design point:** environments are loaded with
`fileset("environments", "*.yaml")` + `yamldecode`, so **adding an environment = adding one YAML file**. This is the hook Backstage uses in step 4.

Use the `argocd-apps` Helm chart for the root app instead of `kubernetes_manifest`, so `plan` does not fail before the Application CRD exists.

**CI (`terraform.yml`):**
- On PR: `terraform fmt -check`, `init -backend=false`, `validate`.
- On merge: create a throwaway kind cluster on the runner, `apply`, run `kubectl get pods -A`, then `destroy`. A hosted runner can't reach your laptop. For a real cluster, use plan on PR and apply on merge against a remote backend, or a self-hosted runner.

**Done when:**
- [ ] `kubectl get ns` shows `argocd`, `dev`, `staging`
- [ ] The Argo CD UI opens at http://localhost:8080 (user `admin`)
- [ ] The `root` app exists (it is OK that it's empty/missing until step 3)
- [ ] The Terraform workflow is green

---

## 2. Two Go services + CI (`orders-svc`, `users-svc`)

**Goal:** two tiny Go HTTP services that build, test and publish images automatically.

**Each service:**
```
cmd/server/main.go     net/http (or chi); endpoints: /healthz, /readyz, /api/<resource>
internal/...           handler + in-memory store + unit tests
Dockerfile             multi-stage: golang builder -> distroless/static, non-root
charts/<svc>/          Helm chart: Deployment, Service, probes, resources, configurable image.tag
.github/workflows/ci.yml
catalog-info.yaml
```

- `orders-svc` calls `users-svc` (for example, validate a user ID via `http://users-svc.<ns>.svc.cluster.local`) so you have a real dependency to see in the catalog.
- Read config from env vars (`PORT`, `USERS_SVC_URL`, `LOG_LEVEL`).
- Use the Helm chart in the app repo as the default. Environment-specific values live in `gitops`.

**CI (`ci.yml`), on push to main:**
1. `go vet`, `go test ./...`, `golangci-lint`.
2. `helm lint charts/<svc>`.
3. Build and push `ghcr.io/<owner>/<svc>:<git-sha>` (docker/build-push-action, `GITHUB_TOKEN` with `packages: write`).
4. Package the chart and push it as an OCI artifact to `oci://ghcr.io/<owner>/charts`. Alternatively, Argo CD can read the chart path from the app repo directly; pick one and document it.
5. Check out `gitops` with `GITOPS_TOKEN`, update `envs/dev/<svc>/values.yaml` → `image.tag: <git-sha>` (use `yq`), then commit and push. Staging is promoted by a PR, not automatically.

On PRs, run steps 1–2 plus a Docker build without pushing.

**`catalog-info.yaml` annotations:**
```yaml
github.com/project-slug: <owner>/orders-svc
backstage.io/kubernetes-id: orders-svc
argocd/app-selector: app.kubernetes.io/name=orders-svc
```
Also set `spec.dependsOn: [component:users-svc]` on orders-svc.

**Done when:**
- [ ] Both images are in GHCR, tagged with the commit SHA
- [ ] Each merge to main produces a commit in `gitops` bumping the dev tag
- [ ] `helm template` renders cleanly for both charts

---

## 3. GitOps CD with Argo CD (`gitops`)

**Goal:** a commit to `gitops` rolls out to the cluster with no manual steps.

**Layout:**
```
apps/                      <- the root app watches this folder (from step 1)
  orders-svc-dev.yaml      Argo CD Application
  orders-svc-staging.yaml
  users-svc-dev.yaml
  users-svc-staging.yaml
envs/
  dev/orders-svc/values.yaml       image.tag, replicas, USERS_SVC_URL ...
  dev/users-svc/values.yaml
  staging/orders-svc/values.yaml
  staging/users-svc/values.yaml
```

Each Application uses **multiple sources**: the chart (OCI from GHCR, or the app repo path) plus `$values/envs/<env>/<svc>/values.yaml` from this repo via `ref: values`. Set the destination namespace = env, enable `syncPolicy.automated` (prune, selfHeal), and add the label `app.kubernetes.io/name=<svc>`.

Optional, once this works: replace the 4 Application files with one **ApplicationSet** (git directory generator over `envs/*/*`). New env/service folders then appear automatically, which makes the Backstage templates simpler.

**Promotion:** dev is updated by CI. Staging is changed by a PR that copies the tag from dev to staging.

**Done when:**
- [ ] All 4 apps are Synced/Healthy in Argo CD
- [ ] Pushing a code change to `orders-svc` updates the dev pods within a few minutes
- [ ] `kubectl -n dev port-forward svc/orders-svc 8081:80` and calling the API works, including the call to users-svc
- [ ] Reverting a commit in `gitops` rolls back the deployment

---

## 4. Backstage on top (`backstage`)

**Goal:** create a new service and a new environment **only from the portal**, and see CI, Argo CD and pod status on each service's page.

### 4a. Base app
- `npx @backstage/create-app@latest`, then run it locally with `yarn start` (http://localhost:3000).
- Switch the database to PostgreSQL (docker compose for local).
- Auth: a GitHub OAuth app + GitHub sign-in resolver.
- Integrations: `integrations.github` with a token (or GitHub App) that can create repos and open PRs.
- Catalog: register `catalog-info.yaml` from all 5 repos (or use the GitHub discovery provider for `<owner>`). Add a `Group` (`platform-team`) and `User` entities.

### 4b. Plugins
| Plugin | Shows |
|---|---|
| GitHub Actions | CI runs on each component page |
| Kubernetes (backend + frontend) | Pods/deployments per env. Configure the kind cluster with a ServiceAccount token. |
| Argo CD (community plugin) | Sync/health status. Configure the Argo CD URL + token. |
| TechDocs | `docs/` + `mkdocs.yml` in each service repo |

### 4c. Software template: "New Go service"
Parameters: name, owner, description, initial environment(s).
Steps:
1. `fetch:template`: a skeleton copied from `orders-svc` with `${{ values.name }}` placeholders (code, Dockerfile, chart, CI, catalog-info).
2. `publish:github`: create `<owner>/<name>`.
3. `fetch:template` + `publish:github:pull-request` to `gitops`: add `apps/<name>-<env>.yaml` and `envs/<env>/<name>/values.yaml`.
4. `catalog:register` for the new repo.
Output: links to the repo, the gitops PR and the catalog entity.

### 4d. Software template: "New environment" (this is how you provision an environment)
Parameters: env name, owner, CPU, memory, max pods, which services to deploy.
Steps:
1. `publish:github:pull-request` to `platform-infra`: add `envs/local/environments/<env>.yaml`. Merging it and running `terraform apply` creates the namespace and quota.
2. `publish:github:pull-request` to `gitops`: add an Application + values for each selected service in `<env>` (or just the values folder, if you use the ApplicationSet).
Output: links to both PRs.

Backstage itself never runs Terraform or kubectl. It only opens PRs, and Terraform plus Argo CD apply them. That keeps everything reviewable and auditable.

### 4e. (Optional) Run Backstage in the cluster
`yarn build:backend`, build the image from `packages/backend/Dockerfile`, push it to GHCR, and deploy it with a Helm chart through Argo CD like any other app (`apps/backstage.yaml`).

**Done when:**
- [ ] The catalog shows all components, dependencies and owners
- [ ] Running "New Go service" creates `payments-svc`, its CI goes green and it appears in dev via Argo CD
- [ ] Running "New environment" for `qa` → merge both PRs → `terraform apply` → the services run in the `qa` namespace
- [ ] Each service page shows its CI runs, Argo CD status and pods

---

## Later (production hardening, not needed for the lab)
- Remote Terraform state (S3/GCS + locking); swap kind for EKS/GKE/AKS behind the same module interface.
- Ingress + cert-manager + external-dns instead of NodePorts/port-forward.
- Secrets: External Secrets Operator or Sealed Secrets; no plaintext tokens in values.
- Argo CD Projects + RBAC per team; SSO for Argo CD and Backstage.
- Image signing (cosign) + SBOM in CI; policy checks (Kyverno/OPA).
- Backstage permissions framework; scorecards (Tech Insights).
