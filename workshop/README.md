# Workshop plan

<p align="center"><img src="assets/txlf-logo-wide.png" alt="Texas Linux Fest, TXLF" width="420"></p>
<p align="center"><strong>Texas Linux Fest 2026 · TXLF2026</strong></p>

[Workshop site in English](index.html) · [Workshop site in Spanish](index.es.html)

## Audience and delivery

<<<<<<< HEAD
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
| 0:30 | [4. Storage](session/04-storage.md) | 15 min | A VM cloned from a golden image in seconds |
| 0:45 | [5. Networking](session/05-networking.md) | 15 min | A container talks to a VM through a Service |
| 1:00 | [6. Day-2 operations](session/06-day2-operations.md) | 20 min | Live migration, node maintenance, snapshot/restore, metrics |
| 1:20 | [7. Trade-offs: one platform for VMs and containers](session/07-tradeoffs-and-wrap-up.md) | 10 min | Trade-offs, containers or VMs, questions |

Each module has a Spanish version (`*.es.md`) next to it. The modules fill the 90 minutes; there is no buffer, so see the instructor guide for what to cut if the room is behind.
=======
**Audience:** Developers, system administrators, and platform engineers with basic Linux and command-line knowledge.  
**Duration:** One 2-hour session (Texas Linux Fest 2026), or modular sessions.  
**Method:** Each module introduces a small set of concepts, demonstrates them, and then gives participants a guided task with a checkpoint.

### Outcomes

Participants will build and inspect an OCI image; deploy and expose container workloads; use persistent storage; explain KubeVirt architecture; operate VM objects; and complete Lab 4: a functional VM.

## Two-hour schedule (Texas Linux Fest 2026)

| Time | Module | Minutes | Main result |
|---|---|---:|---|
| 0:00 | Lab 0 — TexasLinuxFest 2026 | 10 min | Welcome, agenda, and a verified environment |
| 0:10 | 1. Container fundamentals | 10 min | Build, run, inspect, and tag an image |
| 0:20 | 2. Kubernetes fundamentals | 15 min | Deploy and expose a multi-container application |
| 0:35 | 3. Kubernetes networking | 10 min | Test Services and apply an isolation policy |
| 0:45 | 4. Kubernetes storage | 10 min | Demonstrate persistent data across pod replacement |
| 0:55 | 5. KubeVirt concepts | 15 min | Identify VM, VMI, DataVolume, and core components |
| 1:10 | 6. Deploy and manage VMs | 15 min | Create a VM and operate its lifecycle |
| 1:25 | Lab 4 — Functional VM | 25 min | Serve and validate a web page from a Linux VM |
| 1:50 | 7. Operations and next steps | 10 min | Diagnose health, resources, security, and migration readiness |

Times include explanation, guided activity, and discussion, on a pre-installed cluster. In the extended version, each module runs at the pace of its full step-by-step lab guide.
>>>>>>> main

## For instructors

<<<<<<< HEAD
- [Instructor guide](instructor/instructor-guide.md): prepare one cluster per participant with `ansible/` (up to 10 in parallel), the participant sheet, timing, plan B, reset between sessions.
- [Prerequisites](prerequisites.md): cluster readiness checklist.
- The automation itself: [ansible/README.md](../ansible/README.md).

## Export the slides (PDF and PowerPoint)

To share the slides with the organizers, run from the repository root:

```bash
workshop/tools/export-slides.sh
```

It writes `workshop/exports/kubevirt-without-fear-slides-en.pdf` and `.pptx`, plus the same files with `-es` for Spanish. The PDF looks exactly like the web slides; the PowerPoint has editable text in the same colors. It needs Google Chrome (or Chromium or Edge) and [uv](https://docs.astral.sh/uv/) (or `pip install python-pptx`). The `exports/` folder is not committed.

Before the final export, save the QR code of the lab sheet as `workshop/assets/qr/lab-sheet.png` (see [assets/qr/README.md](assets/qr/README.md)). Without it, the Module 1 slide shows an empty QR box.

## Self-paced extras

Six labs, most from the original two-day material, for deeper study after the session. Topics the workshop already covers were removed from them.

| Lab | Topics |
|---|---|
| [1. Containers and Kubernetes](labs/01-foundations.md) | OCI images, container lifecycle, Pods, Deployments, Services |
| [2. Kubernetes networking and storage](labs/02-networking-storage.md) | Services, Ingress, NetworkPolicy, PV/PVC, StorageClass |
| [3. Install KubeVirt](labs/03-kubevirt.md) | Upstream KubeVirt and CDI or OpenShift Virtualization, readiness checks |
| [4. Capstone: a functional VM](labs/04-capstone-functional-vm.md) | CDI import, cloud-init, Service, `curl` validation |
| [5. Operations and troubleshooting](labs/05-operations.md) | Observing VMs, troubleshooting, security, placement |
| [6. OpenShift Virtualization](labs/06-openshift-virtualization.md) | The product operator, HyperConverged, boot images, instance types, console catalog, related operators |

## Lab conventions

- Commands use `kubectl`; on OpenShift, `oc` is equivalent for the Kubernetes operations shown.
- The demo VMs live in the `demo-vms` namespace of each participant cluster.
- Do not put real passwords, private keys, or credentials in manifests or Git. Use SSH public keys.
- Check each module's checkpoint before moving on.
=======
| Module | Topics | Lab |
|---|---|---|
| Lab 0 | Welcome; the 2-hour agenda; tools and environment verification | Verify cluster access, KubeVirt health, and virtctl |
| 1. Containers | Containers vs VMs; OCI images, layers, registries; containerd and CRI-O; Podman/Docker lifecycle | Build a small web image, run it, inspect it, and tag it |
| 2. Kubernetes | Control plane and workers; Pods, Deployments, Services, ConfigMaps, Secrets; declarative YAML; kubectl/oc | Deploy a two-container application and expose it |
| 3. Networking | Pod network and CNI; ClusterIP, NodePort, LoadBalancer; Ingress/Route; NetworkPolicy | Test service discovery and isolate a workload |
| 4. Storage | Ephemeral vs persistent data; PV/PVC; StorageClasses; access and reclaim modes | Write data to a PVC, replace the pod, and verify the data remains |
| 5. KubeVirt | Use cases; virt-api, virt-controller, virt-handler, libvirt; VM/VMI/DataVolume; integration | Inspect platform components and compare a VM with a Deployment |
| 6. VM deployment | Readiness; operator-managed installation; CDI; image sources; network and storage choices; VM lifecycle | Create a VM from an image or DataVolume; start, stop, inspect console, and migrate only if supported |
| 7. Operations | Monitoring; CPU and memory; troubleshooting; security; workload selection; GitOps and advanced topics | Diagnose a provided VM issue and present a remediation |
| Lab 4 · Functional VM | Persistent boot disk; cloud-init; guest service; Kubernetes Service | Deploy a Linux VM that serves an HTTP page and validate it |

## Lab conventions

- Commands use `kubectl`; on OpenShift, `oc` is equivalent for the Kubernetes operations shown. Use `oc` for OpenShift-specific tasks.
- Commands assume a dedicated workshop namespace unless otherwise stated.
- Replace every `CHANGEME` value before applying a template.
- Do not put real passwords, private keys, or credentials in manifests or Git.
- Use an image you are permitted to download and run. A cloud image must support cloud-init for Lab 4.
- Check each lab's validation steps before proceeding.
>>>>>>> main
