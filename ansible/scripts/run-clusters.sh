#!/usr/bin/env bash
# Run one playbook on many clusters, several at a time.
#
#   scripts/run-clusters.sh <playbook.yml> [options] [-- extra ansible args]
#
# Options:
#   -p, --parallel N     clusters at the same time (default 10)
#   -o, --only a,b,c     only these clusters (names from clusters.vault.yml)
#   -s, --skip-login     reuse the kubeconfigs from the last login
#   -r, --runner NAME    ansible-navigator (default) or ansible-playbook
#   -h, --help
#
# Examples:
#   scripts/run-clusters.sh preflight.yml
#   scripts/run-clusters.sh site.yml -- -e confirm_cnv_removal=true
#   scripts/run-clusters.sh site.yml --only lab03,lab07 --skip-login -- -e confirm_cnv_removal=true
#   scripts/run-clusters.sh demo.yml --skip-login -- --tags scale -e clone_count=5
#
# Vault password: set ANSIBLE_VAULT_PASSWORD_FILE, or you'll be asked once.
# Each cluster gets clusters/<name>/{kubeconfig,vars.yml,reports/,logs/}.
set -uo pipefail

ANSIBLE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CLUSTERS_DIR="$ANSIBLE_DIR/clusters"

# --- worker: runs the playbook on one cluster (called through xargs) -----------
if [[ "${1:-}" == "__worker" ]]; then
  shift
  name="$1" playbook="$2" runner="$3" stamp="$4"; shift 4
  cdir="$CLUSTERS_DIR/$name"
  mkdir -p "$cdir/logs"
  log="$cdir/logs/${playbook%.yml}-$stamp.log"
  cd "$ANSIBLE_DIR" || exit 1
  echo "[$(date +%H:%M:%S)] start  $name  ($playbook)"
  if [[ "$runner" == "ansible-navigator" ]]; then
    ansible-navigator run "$playbook" --mode stdout --playbook-artifact-enable false \
      -e "@clusters/$name/vars.yml" "$@" >"$log" 2>&1
  else
    ansible-playbook "$playbook" -e "@clusters/$name/vars.yml" "$@" >"$log" 2>&1
  fi
  rc=$?
  echo "$rc" >"$cdir/logs/${playbook%.yml}-$stamp.rc"
  if [[ $rc -eq 0 ]]; then
    echo "[$(date +%H:%M:%S)] ok     $name"
  else
    echo "[$(date +%H:%M:%S)] FAILED $name (rc=$rc) -> $log"
  fi
  exit 0
fi

usage() { sed -n '2,21p' "$0" | sed 's/^# \{0,1\}//'; exit "${1:-0}"; }

# --- arguments -------------------------------------------------------------------
[[ $# -ge 1 ]] || usage 1
[[ "$1" == "-h" || "$1" == "--help" ]] && usage 0
PLAYBOOK="$1"; shift
PARALLEL=10 ONLY="" SKIP_LOGIN=0 RUNNER="${RUNNER:-ansible-navigator}"
EXTRA=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    -p|--parallel)   PARALLEL="$2"; shift 2 ;;
    -o|--only)       ONLY="$2"; shift 2 ;;
    -s|--skip-login) SKIP_LOGIN=1; shift ;;
    -r|--runner)     RUNNER="$2"; shift 2 ;;
    -h|--help)       usage 0 ;;
    --)              shift; EXTRA=("$@"); break ;;
    *)               echo "Unknown option: $1" >&2; usage 1 ;;
  esac
done

[[ -f "$ANSIBLE_DIR/$PLAYBOOK" ]] || { echo "Playbook not found: $ANSIBLE_DIR/$PLAYBOOK" >&2; exit 1; }
[[ "$PLAYBOOK" == "cluster-login.yml" ]] && { echo "Use the login step of this script, not cluster-login.yml as the playbook." >&2; exit 1; }
command -v "$RUNNER" >/dev/null || { echo "$RUNNER not found (use --runner ansible-playbook?)" >&2; exit 1; }
[[ "$PARALLEL" =~ ^[0-9]+$ && "$PARALLEL" -ge 1 ]] || { echo "--parallel must be a number >= 1" >&2; exit 1; }

cd "$ANSIBLE_DIR" || exit 1

# --- 1. login (once, sequential, the only step that reads the vault) ---------------
if [[ $SKIP_LOGIN -eq 0 ]]; then
  [[ -f clusters.vault.yml ]] || { echo "clusters.vault.yml not found (see clusters.example.yml)" >&2; exit 1; }
  vault_args=()
  if [[ -n "${ANSIBLE_VAULT_PASSWORD_FILE:-}" ]]; then
    vault_args=(--vault-password-file "$ANSIBLE_VAULT_PASSWORD_FILE")
  else
    vault_args=(--ask-vault-pass)
  fi
  echo "== Logging in to the clusters"
  if [[ "$RUNNER" == "ansible-navigator" ]]; then
    ansible-navigator run cluster-login.yml --mode stdout --playbook-artifact-enable false \
      "${vault_args[@]}" -e "cluster_only=$ONLY" || exit 1
  else
    ansible-playbook cluster-login.yml "${vault_args[@]}" -e "cluster_only=$ONLY" || exit 1
  fi
fi

[[ -f "$CLUSTERS_DIR/logged-in.txt" ]] || { echo "No clusters/logged-in.txt: run without --skip-login first." >&2; exit 1; }

# --- 2. pick clusters --------------------------------------------------------------
TARGETS=()
while IFS= read -r n; do
  [[ -z "$n" ]] && continue
  if [[ -n "$ONLY" && ",$ONLY," != *",$n,"* ]]; then continue; fi
  [[ -f "$CLUSTERS_DIR/$n/kubeconfig" ]] || { echo "skip $n: no kubeconfig" >&2; continue; }
  TARGETS+=("$n")
done <"$CLUSTERS_DIR/logged-in.txt"
[[ ${#TARGETS[@]} -gt 0 ]] || { echo "No clusters to run on." >&2; exit 1; }

STAMP="$(date +%Y%m%d-%H%M%S)"
echo "== Running $PLAYBOOK on ${#TARGETS[@]} cluster(s), $PARALLEL at a time: ${TARGETS[*]}"

# --- 3. run in parallel ------------------------------------------------------------
printf '%s\n' "${TARGETS[@]}" | xargs -P "$PARALLEL" -I{} \
  "$0" __worker {} "$PLAYBOOK" "$RUNNER" "$STAMP" ${EXTRA[@]+"${EXTRA[@]}"}

# --- 4. summary --------------------------------------------------------------------
echo
echo "== Summary: $PLAYBOOK ($STAMP)"
printf '%-16s %-8s %s\n' CLUSTER RESULT DETAILS
failed=()
for n in "${TARGETS[@]}"; do
  rcfile="$CLUSTERS_DIR/$n/logs/${PLAYBOOK%.yml}-$STAMP.rc"
  rc="$(cat "$rcfile" 2>/dev/null || echo '?')"
  details="logs/${PLAYBOOK%.yml}-$STAMP.log"
  if [[ "$PLAYBOOK" == "preflight.yml" && -f "$CLUSTERS_DIR/$n/reports/preflight.md" ]]; then
    blockers="$(grep -oE '\*\*[0-9]+ blocker\(s\)\*\*' "$CLUSTERS_DIR/$n/reports/preflight.md" | grep -oE '[0-9]+' || echo 0)"
    warnings="$(grep -c ':warning:' "$CLUSTERS_DIR/$n/reports/preflight.md")"
    details="blockers=$blockers warnings=$warnings  reports/preflight.md"
  fi
  if [[ "$rc" == "0" ]]; then result=ok; else result=FAILED; failed+=("$n"); fi
  printf '%-16s %-8s clusters/%s/%s\n' "$n" "$result" "$n" "$details"
done

if [[ ${#failed[@]} -gt 0 ]]; then
  list="$(IFS=,; echo "${failed[*]}")"
  echo
  echo "Re-run only the failed ones:"
  echo "  scripts/run-clusters.sh $PLAYBOOK --skip-login --only $list ${EXTRA[*]+-- ${EXTRA[*]}}"
  exit 2
fi
