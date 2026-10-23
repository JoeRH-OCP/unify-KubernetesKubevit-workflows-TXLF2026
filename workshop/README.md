# Workshop plan

<p align="center"><img src="assets/txlf-logo-wide.png" alt="Texas Linux Fest — TXLF" width="420"></p>
<p align="center"><strong>Texas Linux Fest 2026 · TXLF2026</strong></p>

[View the visual workshop overview](index.html).

## Audience and delivery

**Audience:** Developers, system administrators, and platform engineers with basic Linux and command-line knowledge.  
**Duration:** Two days (approximately 12 hours of instruction and lab time, excluding breaks), or modular half-day sessions.  
**Method:** Each module introduces a small set of concepts, demonstrates them, and then gives participants a guided task with a checkpoint.

### Outcomes

Participants will build and inspect an OCI image; deploy and expose container workloads; use persistent storage; explain KubeVirt architecture; operate VM objects; and complete a functional VM capstone.

## Two-day schedule

| Day | Module | Suggested time | Main result |
|---|---|---:|---|
| 1 | 1. Container fundamentals | 90–120 min | Build, run, inspect, and tag an image |
| 1 | 2. Kubernetes fundamentals | 120–150 min | Deploy and expose a multi-container application |
| 1 | 3. Kubernetes networking | 90–120 min | Test Services and apply an isolation policy |
| 1 | 4. Kubernetes storage | 90 min | Demonstrate persistent data across pod replacement |
| 2 | 5. KubeVirt concepts | 90 min | Identify VM, VMI, DataVolume, and core components |
| 2 | 6. Deploy and manage VMs | 120–150 min | Create a VM and operate its lifecycle |
| 2 | 7. Operations and next steps | 60–90 min | Diagnose health, resources, security, and migration readiness |
| 2 | Capstone | 90–120 min | Serve and validate a web page from a Linux VM |

Times include guided activity and discussion. Schedule breaks between modules. In a one-day version, use a pre-installed cluster, shorten modules 1–4, and reserve at least 90 minutes for the capstone.

## Module guide

| Module | Topics | Lab |
|---|---|---|
| 1. Containers | Containers vs VMs; OCI images, layers, registries; containerd and CRI-O; Podman/Docker lifecycle | Build a small web image, run it, inspect it, and tag it |
| 2. Kubernetes | Control plane and workers; Pods, Deployments, Services, ConfigMaps, Secrets; declarative YAML; kubectl/oc | Deploy a two-container application and expose it |
| 3. Networking | Pod network and CNI; ClusterIP, NodePort, LoadBalancer; Ingress/Route; NetworkPolicy | Test service discovery and isolate a workload |
| 4. Storage | Ephemeral vs persistent data; PV/PVC; StorageClasses; access and reclaim modes | Write data to a PVC, replace the pod, and verify the data remains |
| 5. KubeVirt | Use cases; virt-api, virt-controller, virt-handler, libvirt; VM/VMI/DataVolume; integration | Inspect platform components and compare a VM with a Deployment |
| 6. VM deployment | Readiness; operator-managed installation; CDI; image sources; network and storage choices; VM lifecycle | Create a VM from an image or DataVolume; start, stop, inspect console, and migrate only if supported |
| 7. Operations | Monitoring; CPU and memory; troubleshooting; security; workload selection; GitOps and advanced topics | Diagnose a provided VM issue and present a remediation |
| Capstone | Persistent boot disk; cloud-init; guest service; Kubernetes Service | Deploy a Linux VM that serves an HTTP page and validate it |

## Lab conventions

- Commands use `kubectl`; on OpenShift, `oc` is equivalent for the Kubernetes operations shown. Use `oc` for OpenShift-specific tasks.
- Commands assume a dedicated workshop namespace unless otherwise stated.
- Replace every `CHANGEME` value before applying a template.
- Do not put real passwords, private keys, or credentials in manifests or Git.
- Use an image you are permitted to download and run. A cloud image must support cloud-init for the capstone.
- Check each lab's validation steps before proceeding.
