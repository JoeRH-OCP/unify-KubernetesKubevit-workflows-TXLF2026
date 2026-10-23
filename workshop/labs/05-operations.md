# Lab 5 — Operations, troubleshooting, and next steps

**Suggested time:** 60–90 minutes  
**Goal:** Use Kubernetes-native tools to inspect VM health, resource allocation, logs, and common failure states.

## Observe the VM and its resources

Use the capstone VM if available:

```bash
kubectl -n kubevirt-workshop get vm,vmi,pods,svc,pvc
kubectl -n kubevirt-workshop describe vm final-functional-vm
kubectl -n kubevirt-workshop describe vmi final-functional-vm
kubectl -n kubevirt-workshop get events --sort-by=.lastTimestamp
```

On OpenShift, inspect the virtualization dashboards and monitoring views available in the cluster. On upstream Kubernetes, use the cluster's configured metrics and logging stack.

Discuss:

- VM desired state versus VMI runtime state.
- CPU and memory requests, limits, scheduling, and guest sizing.
- Node-level capacity versus resources visible inside the guest.
- How to correlate a VM/VMI with the launcher Pod and node.
- Why a VM being `Running` does not prove guest services are healthy.

## Troubleshooting challenge

Instructor changes one condition at a time or provides a prepared broken example. Participants identify evidence before applying a fix.

| Symptom | Evidence to inspect | Likely area |
|---|---|---|
| VM remains Scheduling | `describe vmi`, events, node capacity | Resources, node labels/taints, virtualization support |
| DataVolume import stalls | DV conditions, importer Pod logs/events | URL reachability, TLS, storage provisioning |
| PVC stays Pending | PVC events, StorageClass | Provisioner, capacity, access mode |
| VM runs but HTTP fails | Service endpoints, VMI labels, guest console/cloud-init | Selector, guest service, cloud-init, network |
| VM repeatedly restarts | VMI events, launcher Pod logs, guest boot | Image, disk, node pressure, guest configuration |

Do not expose private keys, cloud-init secrets, or sensitive logs in screenshots or Git commits.

## Security and placement

- Use least-privilege namespace roles for participants; keep cluster administration with instructors.
- Treat guest images as software supply-chain inputs: use trusted sources, verify checksums where available, and track image provenance.
- Avoid embedding passwords or private keys in plain YAML. Use an SSH public key in this lab; use appropriate secret-management controls for production.
- Set realistic CPU and memory requests; apply quotas and monitor contention.
- Select containers for application components that benefit from fast startup and shared-kernel density; select VMs when a guest OS boundary, legacy operating system, or VM-specific workload is required.
- Consider network segmentation and guest firewalling in addition to Kubernetes NetworkPolicy.

## Next steps

- Live migration at scale (only on a cluster configured for it).
- Multus secondary networks and dedicated VM connectivity.
- Windows guests and VirtIO drivers.
- GPU/device passthrough, where supported.
- GitOps workflows for VM templates and DataVolumes.
- Migration tooling and application cutover planning.
