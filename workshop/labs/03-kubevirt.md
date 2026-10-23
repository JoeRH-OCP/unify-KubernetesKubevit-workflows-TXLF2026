# Lab 3 — KubeVirt deployment and VM lifecycle

**Suggested time:** 3.5–4 hours across Modules 5 and 6  
**Goal:** Understand KubeVirt's control plane, confirm installation readiness, and create/manage a VM.

## Module 5 — KubeVirt concepts

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

## Module 6 — Installation and readiness

### OpenShift Virtualization route

Install OpenShift Virtualization from OperatorHub using the release-matched Red Hat documentation. The cluster administrator selects the supported namespace and subscription settings, then creates or verifies the HyperConverged resource. Do not apply upstream KubeVirt installation manifests on this platform.

Instructor checks:

```bash
oc get csv -n openshift-cnv
oc get hco -n openshift-cnv
oc get pods -n openshift-cnv
oc get crd | grep kubevirt
```

### Upstream Kubernetes route

Use the official KubeVirt and CDI installation documentation. These commands illustrate the operator-manifest flow; use a reviewed, pinned release for a repeatable workshop:

```bash
export KUBEVIRT_RELEASE=CHANGEME
kubectl apply -f "https://github.com/kubevirt/kubevirt/releases/download/${KUBEVIRT_RELEASE}/kubevirt-operator.yaml"
kubectl apply -f "https://github.com/kubevirt/kubevirt/releases/download/${KUBEVIRT_RELEASE}/kubevirt-cr.yaml"
kubectl -n kubevirt wait kv/kubevirt --for=condition=Available --timeout=10m
```

Install CDI following its version-matched official guide. Confirm the CDI operator, controller, API server, and upload proxy are ready. Installation and privileged workload requirements are cluster-admin tasks.

**Readiness checkpoint:** KubeVirt reports Available; CDI is healthy; nodes are schedulable; a StorageClass can provision a PVC; and the instructor has tested a VM on this cluster.

## Create and inspect a VM

For a quick smoke test, use the KubeVirt quickstart example appropriate to your environment. For the persistent, application-serving VM required for the workshop outcome, continue to [Lab 4 capstone](04-capstone-functional-vm.md).

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

Only attempt migration if the cluster and VM storage are explicitly configured for it. Otherwise, explain the workflow and inspect migration readiness; do not treat a failed migration on an unprepared lab cluster as a KubeVirt failure.
