# Instructor guide: 90-minute session

This guide covers preparing one cluster per participant (or pair) with the automation in `ansible/`, running the 90 minutes, and resetting between sessions. The full reference for the automation is `ansible/README.md`.

## Timeline

| When | What | Time |
|---|---|---|
| A week before | Order the clusters, fill `clusters.vault.yml`, run preflight on all of them | 1 h |
| The day before | Run `site.yml` on all clusters, check the summary, print the handout cards | 1 to 2 h (unattended) |
| One hour before | Run `reset.yml` + `demo.yml`, then `verify.yml`; open your own demo tabs | 20 min |
| Between sessions | `reset.yml` + `demo.yml` on every cluster | 15 min |
| After the event | `teardown.yml` or return the clusters | 30 min |

## 1. Prepare the clusters

Each Red Hat Demo Platform order gives a console URL, the user `admin` and a random password. Put them in the vault file:

```bash
cd ansible
cp clusters.example.yml clusters.vault.yml
ansible-vault encrypt clusters.vault.yml
ansible-vault edit clusters.vault.yml
```

Use one entry per cluster, with a short name that matches the handout (for example `p01` to `p20`). Then run, from `ansible/`:

```bash
scripts/run-clusters.sh preflight.yml
```

The summary shows blockers and warnings per cluster. Each report is in `clusters/<name>/reports/preflight.md`. On RHDP clusters expect these warnings: OpenShift Virtualization and MTV installed, managed by Argo CD, no NMState instance. They are handled by the next step.

```bash
scripts/run-clusters.sh site.yml --skip-login -- -e confirm_cnv_removal=true -e confirm_mtv_removal=true
```

This removes OpenShift Virtualization and MTV, installs upstream KubeVirt and CDI, kubevirt-manager, the TXLF branding and the demo VMs. It runs 10 clusters at a time; plan about 45 minutes per batch. Re-run only the failed clusters with the command the summary prints.

To keep OpenShift Virtualization on some clusters instead, set `vars: {virt_mode: cnv}` for them in `clusters.vault.yml`. The participant modules work the same; only the KubeVirt version shown changes.

## 2. Handout card per participant

Print one card per cluster:

| Field | Where it comes from |
|---|---|
| Console URL | `console_url` in `clusters.vault.yml` |
| User / password | `admin` / the cluster password (also valid for kubevirt-manager) |
| Landing page | `https://vm-web.apps.<cluster domain>` |
| kubevirt-manager | `https://kubevirt-manager.apps.<cluster domain>` |
| Workshop site | the GitHub Pages URL of this repository |

`clusters/<name>/logs/verify-*.log` lists the two URLs for each cluster.

## 3. Before each session

```bash
scripts/run-clusters.sh reset.yml --skip-login
scripts/run-clusters.sh demo.yml --skip-login
scripts/run-clusters.sh verify.yml --skip-login
```

`--skip-login` reuses the tokens from the last login; they last about 24 hours. Drop it to log in again. All clusters must show 5 VMs `Running`.

Your own laptop, for the projector:
- Console, logged in, with the banner visible.
- The `vm-web` landing page, showing a node.
- kubevirt-manager, logged in.
- A terminal with large font, `KUBECONFIG` pointing to your demo cluster, `virtctl version` matching v1.9.1.

## 4. Running the 90 minutes

| Clock | Module | You do | Checkpoint before moving on |
|---|---|---|---|
| 0:00 | 1. Access | Show the handout, the web terminal, `virtctl` download | Everyone sees 5 VMs `Running` |
| 0:05 | 2. A VM is a Pod | Explain VM / VMI / virt-launcher; live-type `kubectl apply` | `vm-live` Running, SSH works |
| 0:20 | 3. Disks are PVCs | Show `golden-image`, Block/RWX, snapshot clone | `vm-clone-live` DataVolume `Succeeded` |
| 0:35 | 4. Workload migration | Project the landing page during `virtctl migrate`; then snapshot/restore on `vm-web` while they do it on `vm-clone-live` | Node changed; `/srv/data.txt` restored |
| 1:05 | 5. Expose and observe | Service selector, `virtctl expose`, Observe > Metrics, kubevirt-manager graphs | One PromQL query returns data |
| 1:20 | 6. Wrap-up | Recap table, containers vs VMs, next steps, questions | |

If the room is behind, cut Module 4 Part B (cordon) and Module 5's `virtctl expose`. Never cut the live migration: it is the main message of the session.

## 5. Plan B

| Problem | Quick fix |
|---|---|
| A participant cluster is broken | Pair the participant with a neighbor; fix later with `run-clusters.sh site.yml --only <name>` |
| Web terminal does not start | Use the laptop path (`oc login` + `virtctl` download), or pair up |
| `virtctl` download blocked | Use the kubevirt-manager UI for console, start, stop and migrate |
| Migration stuck in `Scheduling` | `kubectl describe vmi vm-web`: usually CPU or memory; migrate a clone instead, or show it on your cluster |
| Docker Hub rate limit (kubevirt-manager image) | Set `kubevirt_manager_image_registry` to a mirror before the event (see `ansible/README.md`) |
| Restore never completes | The VM must be stopped: `virtctl stop`, then `kubectl wait vmi/<name> --for=delete` |

## 6. After the event

```bash
scripts/run-clusters.sh teardown.yml --skip-login -- -e confirm_teardown=true
```

Or simply return the RHDP orders. `teardown.yml` does not reinstall OpenShift Virtualization; Argo CD auto-sync was turned off and its original settings are in `clusters/<name>/reports/argocd-original.yaml`.
