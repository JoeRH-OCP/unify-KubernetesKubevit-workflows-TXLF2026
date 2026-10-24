# Unified Workload Migration with KubeVirt: TXLF 2026

<p align="center">
  <img src="workshop/assets/txlf-logo-wide.png" alt="Texas Linux Fest, TXLF" width="520">
</p>
<p align="center"><strong>Texas Linux Fest 2026 · TXLF2026</strong></p>

<p align="center"><img src="workshop/assets/kubevirt-cluster-hero.png" alt="Kubernetes cluster running container workloads and a persistent Linux virtual machine" width="760"></p>

A 90-minute hands-on workshop: run virtual machines next to containers on Kubernetes with KubeVirt, clone them in seconds, and move them between nodes while they keep serving traffic.

**Duration:** 90 minutes · **Audience:** Linux administrators and anyone curious about VMs on Kubernetes · **Format:** one prepared OpenShift cluster per participant, guided commands with checkpoints

## Workshop material

- [Visual workshop site](workshop/index.html) (Spanish) · [English](workshop/index.en.html)
- [Agenda and module map](workshop/README.md)
- Session modules: [1. Access](workshop/session/01-access.md) · [2. A VM is a Pod](workshop/session/02-vms-are-pods.md) · [3. Disks are PVCs](workshop/session/03-disks-and-clones.md) · [4. Unified workload migration](workshop/session/04-workload-migration.md) · [5. Expose and observe](workshop/session/05-expose-and-observe.md) · [6. Wrap-up](workshop/session/06-wrap-up.md)
- [Instructor guide](workshop/instructor/instructor-guide.md)
- [Self-paced extras](workshop/README.md#self-paced-extras): the original two-day labs

## Cluster automation

[`ansible/`](ansible/README.md) prepares each cluster: upstream KubeVirt and CDI (or keeps OpenShift Virtualization with `virt_mode: cnv`), kubevirt-manager, the TXLF branding and the demo VMs. `ansible/scripts/run-clusters.sh` runs it on many clusters, 10 at a time.

## Platform paths

- **OpenShift:** either OpenShift Virtualization from OperatorHub, or upstream KubeVirt installed by `ansible/` (`virt_mode: kubevirt`, which removes OpenShift Virtualization first). Never both on the same cluster.
- **Upstream Kubernetes:** install KubeVirt and CDI from their official releases with compatible, pinned versions (tested: KubeVirt v1.9.1, CDI v1.66.1 on Kubernetes 1.34).
- **Local clusters:** validate nested virtualization, compute, storage, and networking before class.

See [visual asset credits and details](workshop/assets/README.md). All PNGs used in the workshop have transparent backgrounds.
