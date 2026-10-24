# Workshop plan

<p align="center"><img src="assets/txlf-logo-wide.png" alt="Texas Linux Fest, TXLF" width="420"></p>
<p align="center"><strong>Texas Linux Fest 2026 · TXLF2026</strong></p>

[Workshop site in Spanish](index.html) · [Workshop site in English](index.en.html)

## Audience and delivery

**Audience:** Linux administrators and anyone curious about running virtual machines on Kubernetes. A terminal and basic Linux commands are enough; no prior Kubernetes experience is required.
**Duration:** 90 minutes.
**Format:** One dedicated OpenShift cluster per participant (or pair), prepared by the instructor with `ansible/`. Short explanations, then guided commands with a checkpoint per module.

### Outcomes

Participants create a VM with `kubectl`, clone VM disks in seconds, live-migrate a running VM with no downtime, restore a VM from a snapshot, and expose and monitor VMs with the same Kubernetes tools they use for containers.

## 90-minute agenda

| Clock | Module | Time | Result |
|---|---|---:|---|
| 0:00 | [1. Get access to your cluster](session/01-access.md) | 5 min | `kubectl`, `virtctl` and the demo URLs work |
| 0:05 | [2. A VM is a Pod](session/02-vms-are-pods.md) | 15 min | A VM created with `kubectl apply`, SSH into it |
| 0:20 | [3. Disks are PVCs](session/03-disks-and-clones.md) | 15 min | A VM cloned from a golden image in seconds |
| 0:35 | [4. Unified workload migration](session/04-workload-migration.md) | 30 min | Live migration with no downtime; snapshot and restore |
| 1:05 | [5. Expose and observe](session/05-expose-and-observe.md) | 15 min | Service, Ingress, metrics and events for VMs |
| 1:20 | [6. Wrap-up and next steps](session/06-wrap-up.md) | 10 min | Recap, containers or VMs, questions |

Each module has a Spanish version (`*.es.md`) next to it.

## For instructors

- [Instructor guide](instructor/instructor-guide.md): prepare one cluster per participant with `ansible/` (up to 10 in parallel), handout cards, timing, plan B, reset between sessions.
- [Prerequisites](prerequisites.md): cluster readiness checklist.
- The automation itself: [ansible/README.md](../ansible/README.md).

## Self-paced extras

The original two-day material stays available for deeper study and longer formats:

| Lab | Topics |
|---|---|
| [Lab 1: Container and Kubernetes foundations](labs/01-foundations.md) | Containers vs VMs, OCI images, Pods, Deployments, Services |
| [Lab 2: Kubernetes networking and storage](labs/02-networking-storage.md) | CNI, Services, NetworkPolicy, PV/PVC, StorageClass |
| [Lab 3: KubeVirt deployment and VM lifecycle](labs/03-kubevirt.md) | Components, installation (OpenShift Virtualization or upstream), VM lifecycle |
| [Lab 4 (capstone): deploy a functional Linux VM](labs/04-capstone-functional-vm.md) | CDI import, cloud-init, Service, `curl` validation |
| [Lab 5: Operations, troubleshooting, and next steps](labs/05-operations.md) | Metrics, troubleshooting, security, placement |

## Lab conventions

- Commands use `kubectl`; on OpenShift, `oc` is equivalent for the Kubernetes operations shown.
- The demo VMs live in the `demo-vms` namespace of each participant cluster.
- Do not put real passwords, private keys, or credentials in manifests or Git. Use SSH public keys.
- Check each module's checkpoint before moving on.
