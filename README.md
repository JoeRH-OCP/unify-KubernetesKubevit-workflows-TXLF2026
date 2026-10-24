# Unified Workload Migration with KubeVirt — TXLF 2026

<p align="center">
  <img src="workshop/assets/txlf-logo-wide.png" alt="Texas Linux Fest — TXLF" width="520">
</p>
<p align="center"><strong>Texas Linux Fest 2026 · TXLF2026</strong></p>

<p align="center"><img src="workshop/assets/kubevirt-cluster-hero.png" alt="Kubernetes cluster running container workloads and a persistent Linux virtual machine" width="760"></p>

A hands-on workshop that takes participants from container and Kubernetes fundamentals to deploying and operating a functional virtual machine on Kubernetes with KubeVirt.

**Duration:** One 2-hour session (Texas Linux Fest 2026) or modular sessions · **Audience:** Developers, Linux system administrators, and platform engineers · **Format:** Short theory segments with guided labs

## Workshop material

- [Visual workshop overview](workshop/index.html)
- [Agenda and module map](workshop/README.md)
- [Cluster prerequisites](workshop/prerequisites.md)
- [Lab 0 — TexasLinuxFest 2026: welcome and environment check](workshop/labs/00-texaslinuxfest-2026.md)
- [Lab 1 — Containers and Kubernetes foundations](workshop/labs/01-foundations.md)
- [Lab 2 — Networking and storage](workshop/labs/02-networking-storage.md)
- [Lab 3 — KubeVirt deployment and VM lifecycle](workshop/labs/03-kubevirt.md)
- [Lab 4 — Functional VM: deploy a functional Linux VM](workshop/labs/04-capstone-functional-vm.md)
- [Lab 5 — Operations and troubleshooting](workshop/labs/05-operations.md)
- [Functional VM manifest (Lab 4)](workshop/manifests/capstone-functional-vm.yaml)

## Final exercise — Lab 4 · Functional VM

Participants import a cloud image with CDI, boot a Linux VM with persistent storage, start an HTTP service inside the guest, and validate the page through a Kubernetes Service with `curl`.

Before the lab, replace `CHANGEME_IMAGE_URL` and, if using SSH, `CHANGEME_SSH_PUBLIC_KEY` in the manifest. The cluster must already have KubeVirt or OpenShift Virtualization, CDI, and a working StorageClass.

## Platform paths

- **OpenShift:** Install OpenShift Virtualization from OperatorHub using documentation for the OpenShift release. Do not layer the upstream KubeVirt operator on top.
- **Upstream Kubernetes:** Install KubeVirt and CDI from their official guides with compatible, pinned releases.
- **Local clusters:** Validate nested virtualization, compute, storage, and networking before class.

See [visual asset credits and details](workshop/assets/README.md). All PNGs used in the workshop have transparent backgrounds.
