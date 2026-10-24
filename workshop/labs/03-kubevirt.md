# Lab 3: KubeVirt deployment and VM lifecycle

**Suggested time:** 3.5–4 hours across Modules 5 and 6  
**Goal:** Understand KubeVirt's control plane, confirm installation readiness, and create/manage a VM.

## Module 5: KubeVirt concepts

KubeVirt extends the Kubernetes API with VM resources and runs VM workloads in Pods managed by KubeVirt. Core components include:

- **virt-api:** API extension endpoint for KubeVirt resources.
- **virt-controller:** Watches VM/VMI resources and coordinates lifecycle.
- **virt-handler:** Runs on nodes and manages VMIs assigned to each node.
- **libvirt / QEMU:** VM execution and device management on the node.
- **CDI:** Imports and manages VM disk content into PVCs and DataVolumes.

Key objects:

- **VirtualMachine (VM):** Desired configuration and lifecycle control for a VM.
- **VirtualMachineInstance (VMI):** A running instance of a VM.
- **DataVolume (DV):** CDI resource that imports or clones disk data into storage.
- **PVC:** Persistent disk claim consumed by the VM.

A VM can use a Pod network with masquerade, a Service for stable cluster access, and PVC-backed disks. Multus can add secondary interfaces when the cluster is configured for them.

## Module 6: Installation and readiness

### Two ways to get KubeVirt on OpenShift

- **OpenShift Virtualization:** the supported product, installed from OperatorHub with the release-matched Red Hat documentation. It manages KubeVirt and CDI through the HyperConverged resource.
- **Upstream KubeVirt:** the project releases installed directly. This is what the TXLF 2026 demo clusters use. The automation in `ansible/` installs it with `virt_mode: kubevirt` (and removes OpenShift Virtualization first), or keeps OpenShift Virtualization with `virt_mode: cnv`. Never mix both on the same cluster.

Instructor checks for OpenShift Virtualization:

```bash
oc get csv -n openshift-cnv
oc get hco -n openshift-cnv
oc get pods -n openshift-cnv
oc get crd | grep kubevirt
```

### Upstream Kubernetes route

These are the releases tested for the workshop (Kubernetes 1.34 / OpenShift 4.21). For OpenShift 4.18 (Kubernetes 1.31) use KubeVirt v1.6.6 and CDI v1.63.1.

```bash
export KUBEVIRT_RELEASE=v1.9.1
kubectl apply -f "https://github.com/kubevirt/kubevirt/releases/download/${KUBEVIRT_RELEASE}/kubevirt-operator.yaml"
kubectl apply -f "https://github.com/kubevirt/kubevirt/releases/download/${KUBEVIRT_RELEASE}/kubevirt-cr.yaml"
kubectl -n kubevirt wait kv/kubevirt --for=condition=Available --timeout=10m

export CDI_RELEASE=v1.66.1
kubectl apply -f "https://github.com/kubevirt/containerized-data-importer/releases/download/${CDI_RELEASE}/cdi-operator.yaml"
kubectl apply -f "https://github.com/kubevirt/containerized-data-importer/releases/download/${CDI_RELEASE}/cdi-cr.yaml"
kubectl wait cdi/cdi --for=condition=Available --timeout=10m
```

On OpenShift, `ansible/site.yml` does all of this plus the OpenShift details (Pod Security labels, StorageProfile for Ceph RBD Block/RWX, Ingress). Installation and privileged workload requirements are cluster-admin tasks.

**Readiness checkpoint:** KubeVirt reports Available; CDI is healthy; nodes are schedulable; a StorageClass can provision a PVC; and the instructor has tested a VM on this cluster.

## Create and inspect a VM

For a quick smoke test, apply the ready-made VM from the repository (it uses a Fedora containerDisk and your SSH key, see `ansible/manifests/README.md`):

```bash
kubectl apply -f https://raw.githubusercontent.com/JoeRH-OCP/unify-KubernetesKubevit-workflows-TXLF2026/main/ansible/manifests/01-vm-live.yaml
kubectl get vm,vmi -n demo-vms vm-live
```

For the persistent, application-serving VM required for the workshop outcome, continue to [Lab 4 capstone](04-capstone-functional-vm.md).

Useful commands:

```bash
kubectl get vm,vmi -A
kubectl describe vm CHANGEME
virtctl start CHANGEME
virtctl console CHANGEME
virtctl stop CHANGEME
```

OpenShift users can use `oc` for Kubernetes resources. Install the `virtctl` binary that matches the platform release.

### Guided discussion

1. Compare the VM object with a Deployment: what is desired state, and what is the running instance?
2. Find the virt-handler Pod on a node and inspect its logs (instructor demonstrates elevated access).
3. Identify where the disk image is stored and how a PVC binds to a StorageClass.
4. Compare a containerDisk (convenient, usually ephemeral) with a DataVolume-backed persistent disk.
5. Discuss live migration prerequisites: compatible nodes, migration network/policy, CPU compatibility, and shared or migration-capable storage.

## Optional live migration

Only attempt migration if the cluster and VM storage are explicitly configured for it (RWX disks, two or more schedulable nodes, a common CPU model). The TXLF demo clusters are: see [Module 6 of the 90-minute session](../session/06-day2-operations.md) for the full flow. Otherwise, explain the workflow and inspect migration readiness with the `LiveMigratable` condition; do not treat a failed migration on an unprepared lab cluster as a KubeVirt failure.
