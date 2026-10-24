# Lab 0 — TexasLinuxFest 2026: welcome and environment check

**Suggested time:** 10 minutes  
**Success condition:** You can reach the cluster API, list the nodes, confirm KubeVirt is healthy, and you know your assigned namespace and the 2-hour route.

## Why this lab exists

This workshop compresses the full Unified Workload Migration path into a single 2-hour session. Lab 0 makes sure nobody spends those two hours fighting access problems: we verify the environment once, together, before the content starts.

## The route (2 hours)

| Time | Block | Minutes |
|---|---|---:|
| 0:00 | Lab 0 — TexasLinuxFest 2026 (this lab) | 10 |
| 0:10 | 1. Container foundations | 10 |
| 0:20 | 2. Kubernetes foundations | 15 |
| 0:35 | 3. Kubernetes networking | 10 |
| 0:45 | 4. Kubernetes storage | 10 |
| 0:55 | 5. KubeVirt concepts | 15 |
| 1:10 | 6. Deploy and operate VMs | 15 |
| 1:25 | Lab 4 — Functional VM | 25 |
| 1:50 | 7. Operations and next steps | 10 |

## Steps

1. **Confirm your tools.** You need `kubectl` (or `oc` on OpenShift) and the `virtctl` plugin:

   ```bash
   kubectl version
   virtctl version
   ```

2. **Confirm cluster access.** Log in if your instructor provides a URL and token, then list the nodes:

   ```bash
   kubectl get nodes -o wide
   ```

3. **Confirm KubeVirt is healthy:**

   ```bash
   kubectl get kubevirt -A
   kubectl get pods -n kubevirt
   ```

   On OpenShift, check the HyperConverged operator instead: `kubectl get hco -n openshift-cnv`.

4. **Enter your namespace.** Your instructor assigns one namespace per participant or team:

   ```bash
   kubectl config set-context --current --namespace=kubevirt-workshop
   kubectl get all
   ```

5. **Know the goal.** In Lab 4 you will import a cloud image with CDI, boot a Linux VM with a persistent disk, start an HTTP server inside the guest, and validate it through a Kubernetes Service with `curl`. Every module before it teaches exactly one piece of that exercise.

## If something fails

Raise your hand now — do not wait. Access, capacity, and image-pull problems are environment issues, not participant errors, and the whole session builds on this check.
