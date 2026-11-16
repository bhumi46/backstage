# IDP lab flow diagrams

How a change gets from Backstage to the cluster. See [PLAN.md](../PLAN.md) for the full plan.

## Build order

The order to build the lab in. Each step has to pass its Done when checklist before you start the next one.

```mermaid
flowchart TD
  S0[Step 0: install tools, create 5 repos, set GITOPS_TOKEN] --> C0{All tools print a version and the secret is set?}
  C0 -->|no| S0
  C0 -->|yes| S1[Step 1: Terraform in platform-infra: kind cluster, dev + staging, Argo CD, root app]
  S1 --> C1{argocd, dev, staging exist and Argo CD UI opens on localhost:8080?}
  C1 -->|no| S1
  C1 -->|yes| S2[Step 2: orders-svc + users-svc: Go code, Dockerfile, Helm chart, CI]
  S2 --> C2{Images in GHCR tagged with SHA and CI bumps the dev tag in gitops?}
  C2 -->|no| S2
  C2 -->|yes| S3[Step 3: gitops: 4 Applications + per-env values]
  S3 --> C3{All 4 apps Synced/Healthy and a push reaches dev pods?}
  C3 -->|no| S3
  C3 -->|yes| S4[Step 4: Backstage: catalog, plugins, templates]
  S4 --> C4{payments-svc runs in dev and qa env works from the portal?}
  C4 -->|no| S4
  C4 -->|yes| DONE([Lab complete])
```

## CI pipeline decisions

What ci.yml in each service repo does, depending on the event.

```mermaid
flowchart TD
  E([Push or PR on orders-svc / users-svc]) --> L[go vet, go test, golangci-lint]
  L --> H[helm lint chart]
  H --> OK{Checks pass?}
  OK -->|no| FAIL([CI fails, nothing deploys])
  OK -->|yes| EV{Event type?}
  EV -->|pull request| B[Docker build, no push]
  B --> PRDONE([PR is ready to review])
  EV -->|push to main| P[Build and push image :git-sha to GHCR]
  P --> CH[Package chart, push to oci://ghcr.io/bhumi46/charts]
  CH --> G[Checkout gitops with GITOPS_TOKEN]
  G --> Y[yq: set envs/dev/svc/values.yaml image.tag = git-sha]
  Y --> CM[Commit and push to gitops]
  CM --> AR[Argo CD syncs dev]
  AR --> PROMO{Promote to staging?}
  PROMO -->|yes| SPR[Open PR copying the tag to staging values]
  SPR --> SM[Merge PR, Argo CD syncs staging]
  PROMO -->|not yet| STAY([Stays in dev only])
```

## 1. The whole system

Solid arrows write or deploy. Dotted arrows are Backstage reading status for each service page.

```mermaid
flowchart LR
  Dev([Developer])

  subgraph BS[Backstage portal]
    T1[Template: New Go service]
    T2[Template: New environment]
    CAT[Catalog + plugins]
  end

  subgraph GH[GitHub · bhumi46]
    SVC[orders-svc / users-svc]
    INFRA[platform-infra]
    GITOPS[gitops]
    GHA[GitHub Actions]
    GHCR[(GHCR images + charts)]
  end

  subgraph K8S[kind cluster]
    TF[Terraform apply]
    ARGO[Argo CD root app]
    NS[dev / staging / qa namespaces]
    PODS[Service pods]
  end

  Dev -->|uses| BS
  Dev -->|git push| SVC
  T1 -->|create repo| SVC
  T1 -->|PR: app + values| GITOPS
  T2 -->|PR: env YAML| INFRA
  T2 -->|PR: values per service| GITOPS

  SVC --> GHA
  GHA -->|push image :sha| GHCR
  GHA -->|bump dev image.tag| GITOPS

  INFRA -->|merge| TF
  TF --> NS
  TF -->|bootstraps| ARGO
  GITOPS -->|watched by| ARGO
  ARGO -->|helm + values| PODS
  GHCR -->|pull| PODS
  PODS --- NS

  CAT -.->|CI runs| GHA
  CAT -.->|sync status| ARGO
  CAT -.->|pods| PODS
```

## 2. Code push to running pods

Covers plan steps 2 and 3. Dev deploys automatically; staging is promoted by a PR.

```mermaid
sequenceDiagram
  autonumber
  actor Dev as Developer
  participant Svc as orders-svc repo
  participant CI as GitHub Actions
  participant Reg as GHCR
  participant Git as gitops repo
  participant Argo as Argo CD
  participant K as kind: dev namespace

  Dev->>Svc: push to main
  Svc->>CI: trigger ci.yml
  CI->>CI: go vet, go test, golangci-lint, helm lint
  CI->>Reg: push image orders-svc:git-sha (+ chart)
  CI->>Git: commit envs/dev/orders-svc/values.yaml image.tag = git-sha
  Argo->>Git: detect new commit
  Argo->>K: helm upgrade with dev values
  K->>Reg: pull orders-svc:git-sha
  Note over Git,K: Staging: PR copies the tag from dev to staging values
```

## 3. New Go service from the portal

Plan step 4c. Running the template with `payments-svc` ends with it running in dev.

```mermaid
sequenceDiagram
  autonumber
  actor Dev as Developer
  participant BS as Backstage
  participant New as payments-svc repo
  participant Git as gitops repo
  participant CI as GitHub Actions
  participant Argo as Argo CD

  Dev->>BS: fill in name, owner, envs
  BS->>New: create repo from skeleton (code, Dockerfile, chart, CI)
  BS->>Git: open PR: apps/payments-svc-dev.yaml + values
  BS->>BS: register catalog-info.yaml
  New->>CI: first CI run builds and pushes image
  Dev->>Git: review and merge PR
  Argo->>Git: sees new Application
  Argo->>Argo: deploy payments-svc to dev
```

## 4. New environment from the portal

Plan step 4d. Two PRs: one creates the namespace, the other deploys services into it.

```mermaid
sequenceDiagram
  autonumber
  actor Dev as Developer
  participant BS as Backstage
  participant Infra as platform-infra repo
  participant TF as Terraform
  participant Git as gitops repo
  participant Argo as Argo CD
  participant K as kind cluster

  Dev->>BS: env qa, owner, cpu, memory, max pods, services
  BS->>Infra: PR: envs/local/environments/qa.yaml
  BS->>Git: PR: apps + values for each service in qa
  Dev->>Infra: merge PR
  Dev->>TF: terraform apply
  TF->>K: create qa namespace + quota + limits
  Dev->>Git: merge PR
  Argo->>K: deploy selected services to qa
```

> Backstage never runs Terraform or kubectl. It only creates repos and opens PRs, so every change is reviewed in Git first.
