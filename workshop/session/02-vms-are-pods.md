# Module 2: A VM is a Pod (with QEMU inside)

**Time:** 15 minutes
**Goal:** See how KubeVirt adds virtual machines to the Kubernetes API, create one with `kubectl apply`, and find the Linux pieces you already know: a process, a disk, a network interface.

## Kubernetes learned a new word

KubeVirt is an add-on. It does not replace Kubernetes; it extends it with new resource types:

```bash
kubectl get kubevirt -n kubevirt
kubectl api-resources --api-group=kubevirt.io
```

| Object | Think of it as |
|---|---|
| `VirtualMachine` (VM) | The definition: CPU, memory, disks, NICs, and whether it should be running. Like a Deployment. |
| `VirtualMachineInstance` (VMI) | The VM that is running right now. Like a Pod. |
| `virt-launcher` Pod | The Pod that holds the QEMU process for one VMI. |
| `DataVolume` | A disk image imported or cloned into a PVC by CDI. |

The components run as normal Pods too:

```bash
kubectl get pods -n kubevirt
```

`virt-api` and `virt-controller` are the brains; `virt-handler` runs on every node and talks to libvirt and QEMU there.

## Create a VM with kubectl

Look at the manifest first: it is plain YAML, like any other workload.

```bash
cat manifests/01-vm-live.yaml
kubectl apply -f manifests/01-vm-live.yaml
kubectl get vm,vmi -n demo-vms vm-live -w
```

Press Ctrl+C once the VMI is `Running` (about 30 to 60 seconds). The disk comes from a container image (`containerDisk`), so there was nothing to import.

## Find the Pod and the process

```bash
kubectl get pod -n demo-vms -l vm.kubevirt.io/name=vm-live -o wide
```

That Pod is the VM. Look inside its `compute` container, where libvirt runs QEMU:

```bash
POD=$(kubectl get pod -n demo-vms -l vm.kubevirt.io/name=vm-live -o name)
kubectl exec -n demo-vms $POD -c compute -- virsh list
```

Kubernetes schedules, restarts and limits it like any Pod. CPU and memory requests come from the VM spec.

## Log in to the guest

```bash
virtctl ssh fedora@vm/vm-live -n demo-vms
```

Inside the VM, everything is a normal Fedora system:

```bash
uname -r
ip -br addr
lsblk
exit
```

Two more ways in, without SSH:

```bash
virtctl console vm-quick -n demo-vms
```

The serial console shows the TXLF banner from `/etc/issue`. Exit with Ctrl+].

## Lifecycle: same verbs, new objects

```bash
virtctl stop vm-live -n demo-vms
kubectl get vm,vmi,pod -n demo-vms | grep vm-live
virtctl start vm-live -n demo-vms
```

Stopping removes the VMI and its Pod; the VM object stays, like scaling a Deployment to zero.

## Checkpoint

You created a VM with `kubectl apply`, found its Pod and QEMU process, and logged in to the guest. Next: where its disks live.
