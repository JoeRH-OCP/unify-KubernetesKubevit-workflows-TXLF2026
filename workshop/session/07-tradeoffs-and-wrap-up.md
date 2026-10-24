# Module 7: Trade-offs: one platform for VMs and containers

**Time:** 10 minutes (includes questions)

## What you did in 90 minutes

| Module | You saw that |
|---|---|
| 2. How KubeVirt works | A VM is a Kubernetes object; each running VM is a `virt-launcher` Pod with KVM/QEMU inside |
| 3. VM lifecycle | SSH, consoles, start, stop and restart with `virtctl` and `runStrategy` |
| 4. Storage | Disks are PVCs; images are imported by CDI; clones are CSI snapshots |
| 5. Networking | VMs get Pod IPs, sit behind Services and Ingress, and talk to containers by DNS |
| 6. Day-2 operations | Live migration, node maintenance, snapshot and restore, metrics and events |

## One platform

| Task | Separate stacks | One platform with KubeVirt |
|---|---|---|
| Deploy | Hypervisor console or scripts + Kubernetes YAML | YAML and GitOps for both |
| Access control | Two RBAC models, two audit logs | Kubernetes RBAC and audit for both |
| Networking | VLANs and port groups + Services and Ingress | Services, Ingress and NetworkPolicy for both |
| Storage | Datastores + StorageClasses | StorageClasses and snapshots for both |
| Monitoring | Two tools, two dashboards | Prometheus and the same alerts for both |
| Node patching | Two maintenance procedures | `kubectl drain` moves VMs and reschedules containers |

## The honest trade-offs

| Consider | Why it matters |
|---|---|
| Storage | Live migration needs RWX block storage (Ceph, NFS with care, many SAN CSI drivers). Check your CSI driver first. |
| Skills | VM administrators need Kubernetes basics (Pods, Services, YAML); platform teams need VM basics (guest OS, consoles, sizing). |
| Overhead | Each VM is a Pod plus QEMU: a small memory overhead per VM; plan capacity for it. |
| Feature parity | Most daily features exist; some hypervisor-specific features (for example, some vendor tooling) have different equivalents or none. |
| Support and licensing | Upstream KubeVirt is community-supported; vendor distributions add support. Check guest OS and app licensing per VM. |
| Migration effort | Bringing VMs in needs planning: disk import with CDI for single VMs, Migration Toolkit for Virtualization (Forklift) for fleets from vSphere, oVirt or OpenStack. |

## Containers or VMs?

| Pick a container when | Pick a VM when |
|---|---|
| The app is already packaged as an image | The app needs its own kernel, kernel modules or a different OS |
| You want fast start and high density | It is a vendor appliance or a legacy system you cannot rebuild |
| Scale out is horizontal | The software is licensed or certified per VM |

You do not have to choose for the whole data center: on one platform, each workload moves when it is ready.

## Where to go next

- **KubeVirt user guide:** https://kubevirt.io/user-guide/
- **Instance types and preferences:** VM sizes like cloud flavors (`kubectl get virtualmachineclusterinstancetypes`).
- **Forklift / Migration Toolkit for Virtualization:** bulk migration from vSphere, oVirt and OpenStack.
- **GitOps for VMs:** VMs are YAML, so Argo CD or Flux can manage them.
- **This workshop:** the self-paced extras in the menu go deeper into containers, Kubernetes networking and storage.

## Questions

Your cluster stays available until the instructor resets it. Everything here can be repeated on any cluster with KubeVirt and CDI.

Thank you for attending Texas Linux Fest 2026.
