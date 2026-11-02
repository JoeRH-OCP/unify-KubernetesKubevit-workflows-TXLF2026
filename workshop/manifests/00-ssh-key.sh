#!/usr/bin/env bash
# Creates the Secret that KubeVirt uses to inject your SSH key (accessCredentials).
set -euo pipefail
KEY="${1:-$HOME/.ssh/id_ed25519.pub}"
kubectl -n demo-vms create secret generic demo-ssh-key \
  --from-file=key="$KEY" --dry-run=client -o yaml \
  | kubectl label --local -f - app.kubernetes.io/part-of=txlf-2026 -o yaml \
  | kubectl apply -f -
