# Instructor guide: 90-minute session

This guide covers preparing one cluster per participant (or pair) with the automation in `ansible/`, running the 90 minutes, and resetting between sessions. The full reference for the automation is `ansible/README.md`.

## Timeline

| When | What | Time |
|---|---|---|
| A week before | Order the clusters, fill `clusters.vault.yml`, run preflight on all of them | 1 h |
| The day before | Run `site.yml` on all clusters, check the summary, confirm the participant sheet matches the clusters | 1 to 2 h (unattended) |
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

Use one entry per cluster, with a short name that matches the "Lab" column of the participant sheet (for example `lab01` to `lab20`). Then run, from `ansible/`:

```bash
scripts/run-clusters.sh preflight.yml
```

The summary shows blockers and warnings per cluster. Each report is in `clusters/<name>/reports/preflight.md`. On RHDP clusters expect these warnings: OpenShift Virtualization and MTV installed, managed by Argo CD, no NMState instance. They are handled by the next step.

```bash
scripts/run-clusters.sh site.yml --skip-login -- -e confirm_cnv_removal=true -e confirm_mtv_removal=true
```

This removes OpenShift Virtualization and MTV, installs upstream KubeVirt and CDI, kubevirt-manager, the TXLF branding and the demo VMs. It runs 10 clusters at a time; plan about 45 minutes per batch. Re-run only the failed clusters with the command the summary prints.

To keep OpenShift Virtualization on some clusters instead, set `vars: {virt_mode: cnv}` for them in `clusters.vault.yml`. The participant modules work the same; only the KubeVirt version shown changes.

## 2. The participant sheet

The delivery team creates a Google Sheet with one row per lab cluster (link: TBD). Participants pick a free row and write their name in it during Module 1, so keep the columns simple:

| Column | Content | Filled by |
|---|---|---|
| Lab | `lab01` to `lab20`, same names as in `clusters.vault.yml` | Delivery team |
| Console URL | `console_url` of the cluster | Delivery team |
| User | `admin` | Delivery team |
| Password | The cluster password (also valid for kubevirt-manager) | Delivery team |
| Participant | Name of the person (or pair) using it | Participant (column name TBD) |

Optional columns: the landing page (`https://vm-web.apps.<cluster domain>`) and kubevirt-manager (`https://kubevirt-manager.apps.<cluster domain>`) URLs. `clusters/<name>/logs/verify-*.log` lists both for each cluster.

The sheet holds admin passwords. Share the link only in the room (screen and session chat), keep editing limited to the "Participant" column if possible, and delete the sheet or rotate the clusters after the event.

## 3. Before each session

```bash
scripts/run-clusters.sh reset.yml --skip-login
scripts/run-clusters.sh demo.yml --skip-login
scripts/run-clusters.sh verify.yml --skip-login
```

`--skip-login` reuses the tokens from the last login; they last about 24 hours. Drop it to log in again. All clusters must show 5 VMs `Running`.

On one participant cluster, open the web terminal and run Module 1 end to end. Check that `git` and `ssh-keygen` exist there (`git --version; ssh-keygen -V`); if `git` is missing, Module 1 has a `curl | tar` fallback.

Your own laptop, for the projector:
- Console, logged in, with the banner visible.
- The `vm-web` landing page, showing a node.
- kubevirt-manager, logged in.
- A terminal with large font, `KUBECONFIG` pointing to your demo cluster, `virtctl version` matching v1.9.1.

## 4. Running the 90 minutes

| Clock | Module | You do | Checkpoint before moving on |
|---|---|---|---|
| 0:00 | 1. Access from your browser | Show the participant sheet, the web terminal, the repo clone and `virtctl` in the web terminal (nothing on laptops) | Everyone sees 5 VMs `Running` |
| 0:05 | 2. How KubeVirt works | The "worries" table, VM / VMI / virt-launcher; live-type `kubectl apply`; use cases | `vm-live` Running |
| 0:20 | 3. VM lifecycle | SSH, serial console, stop/start/restart, `runStrategy` | SSH into `vm-live` works |
| 0:30 | 4. Storage | `golden-image`, Block/RWX, snapshot clone | `vm-clone-live` DataVolume `Succeeded` |
| 0:45 | 5. Networking | Pod IP, Service selector, a container calling the VM, `virtctl expose` | The `curl` container gets `200` |
| 1:00 | 6. Day-2 operations | Project the landing page during `virtctl migrate`; cordon; snapshot/restore on `vm-web` while they do it on `vm-clone-live`; Observe > Metrics; 1-minute mention of "Day 2 with Ansible" (read only, not run) | Node changed; `/srv/data.txt` restored |
| 1:20 | 7. Trade-offs: one platform for VMs and containers | One-platform table, honest trade-offs, containers or VMs, questions | |

There is no buffer: the seven modules fill the 90 minutes. If the room is behind, cut the cordon step and the metrics queries in Module 6, and `virtctl expose` in Module 5. Never cut the live migration or the trade-offs: they are what the abstract promises.

## 5. Plan B

| Problem | Quick fix |
|---|---|
| A participant cluster is broken | Pair the participant with a neighbor; fix later with `run-clusters.sh site.yml --only <name>` |
| Web terminal does not start | Pair up; as a last resort, `oc login` from a laptop terminal |
| `virtctl` download blocked | Use the kubevirt-manager UI for console, start, stop and migrate |
| `quay.io/curl/curl` cannot be pulled (Module 5) | `kubectl run` with any image that has curl, or show it on your cluster |
| Migration stuck in `Scheduling` | `kubectl describe vmi vm-web`: usually CPU or memory; migrate a clone instead, or show it on your cluster |
| Docker Hub rate limit (kubevirt-manager image) | Set `kubevirt_manager_image_registry` to a mirror before the event (see `ansible/README.md`) |
| Restore never completes | The VM must be stopped: `virtctl stop`, then `kubectl wait vmi/<name> --for=delete` |

## 6. After the event

```bash
scripts/run-clusters.sh teardown.yml --skip-login -- -e confirm_teardown=true
```

Or simply return the RHDP orders. `teardown.yml` does not reinstall OpenShift Virtualization; Argo CD auto-sync was turned off and its original settings are in `clusters/<name>/reports/argocd-original.yaml`.
