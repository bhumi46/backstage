#!/usr/bin/env bash
# Create/update the Secret backstage-secrets (namespace backstage) that the in-cluster Backstage reads
# (charts/backstage, step 4e). Values come from .env and are never printed or committed.
# The cluster's own ServiceAccount replaces K8S_SA_TOKEN, so that one is not copied.
# Usage: scripts/cluster-secrets.sh [path/to/platform-infra/envs/local]
set -euo pipefail
cd "$(dirname "$0")/.."
TF_DIR=${1:-../platform-infra/envs/local}
ENV_FILE=.env
NAMESPACE=backstage
KEYS=(GITHUB_TOKEN AUTH_GITHUB_CLIENT_ID AUTH_GITHUB_CLIENT_SECRET ARGOCD_AUTH_TOKEN
      POSTGRES_USER POSTGRES_PASSWORD BACKSTAGE_TEST_TOKEN)

[ -f "$ENV_FILE" ] || { echo "missing $ENV_FILE (cp .env.example .env)" >&2; exit 1; }
KUBECONFIG=$(terraform -chdir="$TF_DIR" output -raw kubeconfig_path) && export KUBECONFIG

umask 077
TMP=$(mktemp); trap 'rm -f "$TMP"' EXIT
for k in "${KEYS[@]}"; do
  line=$(grep -E "^$k=" "$ENV_FILE" | tail -1 || true)
  [ -n "${line#*=}" ] || { echo "$k is empty in $ENV_FILE" >&2; exit 1; }
  printf '%s\n' "$line" >> "$TMP"
done

kubectl -n "$NAMESPACE" create secret generic backstage-secrets --from-env-file="$TMP" \
  --dry-run=client -o yaml | kubectl apply -f - >/dev/null
echo "secret $NAMESPACE/backstage-secrets updated with: ${KEYS[*]}"
