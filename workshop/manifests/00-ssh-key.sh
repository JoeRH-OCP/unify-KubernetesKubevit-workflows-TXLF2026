#!/usr/bin/env bash
# Adds your SSH public key to the Secret that KubeVirt injects into the VMs
# (accessCredentials). Creates the key pair first if you don't have one.
#
# Safe for shared clusters: each person's key is stored as its own entry, so
# running it again, or from another terminal, adds a key and never removes one.
# VMs get every key in the Secret when they boot.
#
#   ./manifests/00-ssh-key.sh                  # default key, namespace demo-vms
#   NS=my-ns ./manifests/00-ssh-key.sh         # another namespace
#   ./manifests/00-ssh-key.sh path/to/key.pub  # another public key
set -euo pipefail
NS="${NS:-demo-vms}"
SECRET=demo-ssh-key
KEY="${1:-$HOME/.ssh/id_ed25519.pub}"

if [ ! -f "$KEY" ]; then
  if [ $# -gt 0 ]; then
    echo "Public key not found: $KEY" >&2
    exit 1
  fi
  mkdir -p ~/.ssh && chmod 700 ~/.ssh
  ssh-keygen -q -t ed25519 -N '' -f "${KEY%.pub}"
  echo "Created a new SSH key: ${KEY%.pub}"
fi

# Entry name from a hash of the key: the same key always lands in the same entry.
sha() { if command -v sha256sum >/dev/null; then sha256sum; else shasum -a 256; fi; }
ENTRY="key-$(awk '{print $2}' "$KEY" | sha | cut -c1-12)"
PUB="$(tr -d '\n' < "$KEY")"

if kubectl -n "$NS" get secret "$SECRET" >/dev/null 2>&1; then
  kubectl -n "$NS" patch secret "$SECRET" --type merge \
    -p "{\"stringData\":{\"$ENTRY\":\"$PUB\"}}" >/dev/null
else
  kubectl -n "$NS" create secret generic "$SECRET" --from-literal="$ENTRY=$PUB" >/dev/null
  kubectl -n "$NS" label secret "$SECRET" app.kubernetes.io/part-of=txlf-2026 >/dev/null
fi

COUNT=$(kubectl -n "$NS" get secret "$SECRET" -o go-template='{{len .data}}')
echo "Your key is in Secret $SECRET ($NS) as $ENTRY. Keys stored: $COUNT."
