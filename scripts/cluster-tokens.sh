#!/usr/bin/env bash
# Copy cluster credentials for the Kubernetes and Argo CD plugins into .env, without printing them.
#   K8S_CLUSTER_URL, K8S_SA_TOKEN  <- platform-infra terraform outputs (read-only ServiceAccount)
#   ARGOCD_AUTH_TOKEN              <- new API token for the read-only Argo CD account "backstage"
#   BACKSTAGE_TEST_TOKEN           <- random; only used by the gitignored app-config.local.yaml
# Re-run after recreating the cluster. Usage: scripts/cluster-tokens.sh [path/to/platform-infra/envs/local]
set -euo pipefail
cd "$(dirname "$0")/.."
TF_DIR=${1:-../platform-infra/envs/local}
ARGOCD_URL=${ARGOCD_URL:-http://localhost:8080}
ENV_FILE=.env
[ -f "$ENV_FILE" ] || { echo "missing $ENV_FILE (cp .env.example .env)" >&2; exit 1; }

set_kv() { # set_kv KEY VALUE  -> replaces or appends KEY=VALUE in .env
  local tmp; tmp=$(mktemp)
  grep -v "^$1=" "$ENV_FILE" > "$tmp" || true
  printf '%s=%s\n' "$1" "$2" >> "$tmp"
  cat "$tmp" > "$ENV_FILE"; rm -f "$tmp"
}

tf() { terraform -chdir="$TF_DIR" output -raw "$1"; }

set_kv K8S_CLUSTER_URL "$(tf kube_api_url)"
set_kv K8S_SA_TOKEN "$(tf backstage_k8s_sa_token)"

KUBECONFIG=$(tf kubeconfig_path) && export KUBECONFIG
ADMIN_PW=$(kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d)
SESSION=$(jq -n --arg p "$ADMIN_PW" '{username:"admin",password:$p}' |
  curl -fsS -H 'Content-Type: application/json' -d @- "$ARGOCD_URL/api/v1/session" | jq -r .token)
ARGO_TOKEN=$(curl -fsS -X POST -H "Authorization: Bearer $SESSION" -H 'Content-Type: application/json' \
  -d '{"name":"backstage"}' "$ARGOCD_URL/api/v1/account/backstage/token" | jq -r .token)
[ -n "$ARGO_TOKEN" ] && [ "$ARGO_TOKEN" != null ] || { echo "failed to create Argo CD token" >&2; exit 1; }
set_kv ARGOCD_AUTH_TOKEN "$ARGO_TOKEN"

grep -qE '^BACKSTAGE_TEST_TOKEN=.+' "$ENV_FILE" || set_kv BACKSTAGE_TEST_TOKEN "$(openssl rand -hex 24)"
echo "updated $ENV_FILE: K8S_CLUSTER_URL K8S_SA_TOKEN ARGOCD_AUTH_TOKEN BACKSTAGE_TEST_TOKEN"
