# Module 6: Wrap-up and next steps

**Time:** 10 minutes (includes questions)

## What you did in 90 minutes

| Module | You saw that |
|---|---|
| 2. A VM is a Pod | KubeVirt adds VM objects to the Kubernetes API; each running VM is a `virt-launcher` Pod with QEMU inside |
| 3. Disks are PVCs | Images are imported by CDI; clones are CSI snapshots, ready in seconds |
| 4. Workload migration | Running VMs move between nodes with no downtime, follow node maintenance rules, and roll back from snapshots; existing VMs come in through CDI or MTV |
| 5. Expose and observe | VMs use the same Services, Ingress, metrics and events as containers |

Everything ran on upstream projects with standard Kubernetes APIs: KubeVirt v1.9.1, CDI v1.66.1, kubevirt-manager, Ceph RBD through CSI.

## Containers or VMs?

| Pick a container when | Pick a VM when |
|---|---|
| The app is already packaged as an image | The app needs its own kernel, kernel modules or a different OS |
| You want fast start and high density | It is a vendor appliance or a legacy system you cannot rebuild |
| Scale out is horizontal | The software is licensed or certified per VM |

On one platform you do not have to choose for the whole data center: each workload can move when it is ready.

## Where to go next

- **KubeVirt user guide:** https://kubevirt.io/user-guide/
- **Instance types and preferences:** VM sizes like cloud flavors (`kubectl get virtualmachineclusterinstancetypes`).
- **Migration Toolkit for Virtualization / Forklift:** bulk migration from vSphere, oVirt and OpenStack.
- **GitOps for VMs:** VMs are YAML, so Argo CD or Flux can manage them.
- **Windows guests, GPUs and SR-IOV:** in the self-paced extras and the KubeVirt docs.
- **This workshop:** the self-paced extras in the menu go deeper into containers, Kubernetes networking and storage.

## Questions

Your cluster stays available until the instructor resets it. Everything in `ansible/manifests/` and these modules can be repeated on any cluster with KubeVirt and CDI.

Thank you for attending Texas Linux Fest 2026.
