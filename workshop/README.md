# Workshop plan

<p align="center"><img src="assets/txlf-logo-wide.png" alt="Texas Linux Fest, TXLF" width="420"></p>
<p align="center"><strong>Texas Linux Fest 2026 · TXLF2026</strong></p>

[Workshop site in Spanish](index.html) · [Workshop site in English](index.en.html)

## Audience and delivery

**Session:** KubeVirt Without Fear: Running VMs and Containers Together on One Platform.
**Audience:** Linux administrators and anyone curious about running virtual machines on Kubernetes. A terminal and basic Linux commands are enough; no prior Kubernetes experience is required.
**Duration:** 90 minutes.
**Format:** Bring a laptop; everything runs in the browser (OpenShift console and web terminal), so any operating system works. One dedicated cluster per participant (or pair), prepared by the instructor with `ansible/`.

### Outcomes

Participants understand how KubeVirt works and what it solves; manage the VM lifecycle; use Kubernetes storage and networking for VMs (including a container talking to a VM); run day-2 operations (live migration, node maintenance, snapshot and restore, metrics); and weigh the practical trade-offs of one control plane for legacy and modern applications.

## 90-minute agenda

| Clock | Module | Time | Result |
|---|---|---:|---|
| 0:00 | [1. Get access from your browser](session/01-access.md) | 5 min | Web terminal, `virtctl` and the demo URLs ready |
| 0:05 | [2. How KubeVirt works](session/02-how-kubevirt-works.md) | 15 min | A VM created with `kubectl apply`; its Pod and QEMU process found |
| 0:20 | [3. VM lifecycle](session/03-vm-lifecycle.md) | 10 min | SSH, consoles, start/stop/restart, `runStrategy` |
| 0:30 | [4. Storage](session/04-storage.md) | 12 min | A VM cloned from a golden image in seconds |
| 0:42 | [5. Networking](session/05-networking.md) | 12 min | A container talks to a VM through a Service |
| 0:54 | [6. Day-2 operations](session/06-day2-operations.md) | 20 min | Live migration, node maintenance, snapshot/restore, metrics |
| 1:14 | [7. Trade-offs and one control plane](session/07-tradeoffs-and-wrap-up.md) | 10 min | Trade-offs, containers or VMs, questions |

Each module has a Spanish version (`*.es.md`) next to it. The last 6 minutes are buffer.

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
