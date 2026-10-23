# Lab environment prerequisites

## Recommended environment

Use a pre-installed OpenShift cluster with a compatible, healthy OpenShift Virtualization installation. This gives the workshop a consistent path for operator lifecycle, storage, networking, VM console access, and troubleshooting.

A supported upstream Kubernetes cluster with KubeVirt and CDI is also suitable. Follow the upstream installation guides for the exact Kubernetes and KubeVirt versions. Avoid mixing the OpenShift Virtualization operator with upstream KubeVirt installation instructions.

## Cluster readiness checklist

Complete these checks before the workshop starts.

### Access and tools

- A named participant account with permission to create and view Pods, Deployments, Services, ConfigMaps, Secrets, PVCs, VMs, and VMIs in the lab namespace.
- Cluster-admin access reserved for the instructor during installation and cluster-level troubleshooting.
- `kubectl` or `oc`; `virtctl` matching the installed virtualization release.
- Podman or Docker for the container lab.
- A terminal with YAML editing, curl, and basic shell tools.
- Working DNS, image registry access, and outbound access to the selected VM image source.

### Compute and virtualization support

- Worker nodes with CPU virtualization support (Intel VT-x or AMD-V) exposed to the node operating system.
- BIOS/firmware virtualization enabled on the physical or virtual host.
- Sufficient CPU and memory capacity for the cluster plus each concurrently running guest. For the capstone, reserve at least 1 vCPU and 2 GiB RAM per participant VM, plus overhead.
- For nested or cloud environments, verify that the provider and host configuration expose hardware virtualization. If emulation is used for a learning-only environment, expect slower performance and verify support in the chosen KubeVirt release documentation.

### Storage

- A working default StorageClass, or an explicitly selected class for the lab.
- Dynamic PVC provisioning that can create a boot disk of at least 20 GiB for each participant.
- CDI installed and healthy for importing the capstone qcow2 image.
- Sufficient free capacity and a reclaim policy understood by the instructor.
- For live migration exercises, shared storage and migration-compatible access modes/configuration are required; otherwise treat migration as a discussion or instructor demonstration.

### Networking

- Pod networking and DNS functioning between workloads.
- Service networking available.
- Ingress/Route access only if the lab environment exposes it.
- NetworkPolicy enforcement only if the cluster CNI implements it.
- For the capstone, the VM must use the default Pod network with masquerade; a Kubernetes Service plus port-forward provides the simplest repeatable HTTP check.
- Multus and secondary networks are optional advanced material and require a prepared NetworkAttachmentDefinition and suitable node networking.

### Platform-specific readiness

**OpenShift**
- OpenShift Virtualization installed from OperatorHub using the documentation matching the OpenShift release.
- The HyperConverged resource reports ready and virtualization pods are healthy.
- The participant role permits namespaced VM creation; necessary SCC and cluster configuration are managed by the platform operator.

**Upstream Kubernetes**
- KubeVirt and CDI are installed with compatible versions.
- KubeVirt reports Available and CDI components are ready.
- Nodes satisfy KubeVirt requirements and admission/security policies permit the required virtualization workloads.

## Instructor preflight

Run these checks with an account that can inspect cluster resources:

```bash
kubectl get nodes -o wide
kubectl get storageclass
kubectl get pods -A | grep -E 'kubevirt|virt-|cdi|data-importer'
kubectl get crd | grep -E 'kubevirt|cdi'
```

For OpenShift:

```bash
oc get hco -A
oc get pods -n openshift-cnv
oc get storageclass
oc get nodes -o wide
```

Confirm that the instructor has selected a cloud-init-capable qcow2 image URL and that the cluster can retrieve it. Test the image import and one full capstone VM at least one day before delivery.

## Participant namespace and quota

Create one namespace per participant or small team. Apply quotas appropriate to the cluster. A starting point per participant is 2 vCPU and 4 GiB memory for the guest, plus 20–30 GiB storage, subject to platform capacity and policy. Avoid cluster-wide permissions for participants.

## Known limitations

- Local clusters frequently lack nested virtualization or enough RAM for concurrent VMs.
- Managed Kubernetes services may not expose the host virtualization capabilities KubeVirt needs.
- NetworkPolicy behavior depends on the CNI implementation.
- Storage and live migration behavior depends on the backend and access modes.
- A successful API deployment does not prove that a VM can schedule; validate a real guest before class.
