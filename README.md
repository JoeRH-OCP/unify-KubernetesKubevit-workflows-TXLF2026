# KubeVirt Without Fear: Running VMs and Containers Together on One Platform

<p align="center">
  <img src="workshop/assets/txlf-logo-wide.png" alt="Texas Linux Fest, TXLF" width="520">
</p>
<p align="center"><strong>Texas Linux Fest 2026 · TXLF2026</strong></p>

<p align="center"><img src="workshop/assets/kubevirt-cluster-hero.png" alt="Kubernetes cluster running container workloads and a persistent Linux virtual machine" width="760"></p>

A 90-minute hands-on workshop at Texas Linux Fest 2026. KubeVirt lets organizations run virtual machines and containers side by side on Kubernetes. This session removes the confusion and fear around it: how KubeVirt works, what it solves, VM lifecycle, networking, storage, day-2 operations, and the practical trade-offs of one control plane for legacy and modern applications.

**Duration:** 90 minutes · **Audience:** Linux administrators and anyone curious about VMs on Kubernetes · **Format:** bring a laptop; all exercises run in the browser, one prepared cluster per participant

## Workshop material

- [Visual workshop site](workshop/index.html) (Spanish) · [English](workshop/index.en.html)
- [Agenda and module map](workshop/README.md)
- Session modules: [1. Access](workshop/session/01-access.md) · [2. How KubeVirt works](workshop/session/02-how-kubevirt-works.md) · [3. VM lifecycle](workshop/session/03-vm-lifecycle.md) · [4. Storage](workshop/session/04-storage.md) · [5. Networking](workshop/session/05-networking.md) · [6. Day-2 operations](workshop/session/06-day2-operations.md) · [7. Trade-offs](workshop/session/07-tradeoffs-and-wrap-up.md)
- [Instructor guide](workshop/instructor/instructor-guide.md)
- [Self-paced extras](workshop/README.md#self-paced-extras): the original two-day labs

## Cluster automation

[`ansible/`](ansible/README.md) prepares each cluster: upstream KubeVirt and CDI (or keeps OpenShift Virtualization with `virt_mode: cnv`), kubevirt-manager, the TXLF branding and the demo VMs. `ansible/scripts/run-clusters.sh` runs it on many clusters, 10 at a time.

## Platform paths

- **OpenShift:** either OpenShift Virtualization from OperatorHub, or upstream KubeVirt installed by `ansible/` (`virt_mode: kubevirt`, which removes OpenShift Virtualization first). Never both on the same cluster.
- **Upstream Kubernetes:** install KubeVirt and CDI from their official releases with compatible, pinned versions (tested: KubeVirt v1.9.1, CDI v1.66.1 on Kubernetes 1.34).
- **Local clusters:** validate nested virtualization, compute, storage, and networking before class.

See [visual asset credits and details](workshop/assets/README.md). All PNGs used in the workshop have transparent backgrounds.
