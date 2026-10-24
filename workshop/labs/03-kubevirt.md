# Lab 3: Install KubeVirt and check readiness

**Suggested time:** 60–90 minutes  
**Goal:** Install KubeVirt and CDI on a cluster and confirm it is ready for VMs. How KubeVirt works and the VM lifecycle are covered in [Modules 2 and 3 of the workshop](../session/02-how-kubevirt-works.md).

## Installation and readiness

### Two ways to get KubeVirt on OpenShift

- **OpenShift Virtualization:** the supported product, installed from OperatorHub with the release-matched Red Hat documentation ([Lab 6](06-openshift-virtualization.md) walks through it). It manages KubeVirt and CDI through the HyperConverged resource.
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

## Next

- First VM on the new cluster: [Module 2 of the session](../session/02-how-kubevirt-works.md) (`manifests/01-vm-live.yaml`).
- A persistent VM that serves an application: [Lab 4 capstone](04-capstone-functional-vm.md).
- Live migration and node maintenance: [Module 6 of the session](../session/06-day2-operations.md).
