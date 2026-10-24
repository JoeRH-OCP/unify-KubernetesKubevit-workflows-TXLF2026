# KubeVirt Without Fear: Running VMs and Containers Together on One Platform

<p align="center">
  <img src="workshop/assets/txlf-logo-wide.png" alt="Texas Linux Fest, TXLF" width="520">
</p>
<p align="center"><strong>Texas Linux Fest 2026 · TXLF2026</strong></p>

<p align="center"><img src="workshop/assets/kubevirt-cluster-hero.png" alt="Kubernetes cluster running container workloads and a persistent Linux virtual machine" width="760"></p>

A 90-minute hands-on workshop at Texas Linux Fest 2026. KubeVirt lets organizations run virtual machines and containers side by side on Kubernetes. This session removes the confusion and fear around it: how KubeVirt works, what it solves, VM lifecycle, networking, storage, day-2 operations, and the practical trade-offs of one control plane for legacy and modern applications.

**Duration:** One 2-hour session (Texas Linux Fest 2026) or modular sessions · **Audience:** Developers, Linux system administrators, and platform engineers · **Format:** Short theory segments with guided labs

## Workshop material

- [Visual workshop site](workshop/index.html) (English) · [Español](workshop/index.es.html)
- [Agenda and module map](workshop/README.md)
<<<<<<< HEAD
- Session modules: [1. Access](workshop/session/01-access.md) · [2. How KubeVirt works](workshop/session/02-how-kubevirt-works.md) · [3. VM lifecycle](workshop/session/03-vm-lifecycle.md) · [4. Storage](workshop/session/04-storage.md) · [5. Networking](workshop/session/05-networking.md) · [6. Day-2 operations](workshop/session/06-day2-operations.md) · [7. Trade-offs](workshop/session/07-tradeoffs-and-wrap-up.md)
- [Instructor guide](workshop/instructor/instructor-guide.md)
- [Self-paced extras](workshop/README.md#self-paced-extras): the original two-day labs

## Cluster automation
=======
- [Cluster prerequisites](workshop/prerequisites.md)
- [Lab 0 — TexasLinuxFest 2026: welcome and environment check](workshop/labs/00-texaslinuxfest-2026.md)
- [Lab 1 — Containers and Kubernetes foundations](workshop/labs/01-foundations.md)
- [Lab 2 — Networking and storage](workshop/labs/02-networking-storage.md)
- [Lab 3 — KubeVirt deployment and VM lifecycle](workshop/labs/03-kubevirt.md)
- [Lab 4 — Functional VM: deploy a functional Linux VM](workshop/labs/04-capstone-functional-vm.md)
- [Lab 5 — Operations and troubleshooting](workshop/labs/05-operations.md)
- [Functional VM manifest (Lab 4)](workshop/manifests/capstone-functional-vm.yaml)

## Final exercise — Lab 4 · Functional VM
>>>>>>> main

[`ansible/`](ansible/README.md) prepares each cluster: upstream KubeVirt and CDI (or keeps OpenShift Virtualization with `virt_mode: cnv`), kubevirt-manager, the TXLF branding and the demo VMs. `ansible/scripts/run-clusters.sh` runs it on many clusters, 10 at a time.

## Platform paths

- **OpenShift:** either OpenShift Virtualization from OperatorHub, or upstream KubeVirt installed by `ansible/` (`virt_mode: kubevirt`, which removes OpenShift Virtualization first). Never both on the same cluster.
- **Upstream Kubernetes:** install KubeVirt and CDI from their official releases with compatible, pinned versions (tested: KubeVirt v1.9.1, CDI v1.66.1 on Kubernetes 1.34).
- **Local clusters:** validate nested virtualization, compute, storage, and networking before class.

See [visual asset credits and details](workshop/assets/README.md). All PNGs used in the workshop have transparent backgrounds.
