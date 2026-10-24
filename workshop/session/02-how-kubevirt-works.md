# Module 2: How KubeVirt works (a VM is a Pod)

**Time:** 15 minutes
**Goal:** Remove the mystery: see what KubeVirt adds to Kubernetes, create a VM with `kubectl apply`, and find the Linux pieces you already know behind it.

## What KubeVirt is (and is not)

KubeVirt is an open source add-on for Kubernetes, a CNCF project. It does not replace your hypervisor knowledge: under the hood it uses the same KVM, QEMU and libvirt you find on any Linux virtualization host. What changes is who drives them: the Kubernetes API.

Common worries, and the short answers:

| Worry | Reality |
|---|---|
| "My VMs become containers" | No. The guest is a full VM with its own kernel, booting a normal OS image. |
| "It is slow or emulated" | No. It uses KVM hardware virtualization, like any Linux hypervisor. |
| "I have to rewrite my apps" | No. The VM runs the same OS and app; only the way you manage it changes. |
| "I lose my VM features" | Live migration, snapshots, clones, consoles, cloud-init and multiple NICs are all there. |

## Kubernetes learned a new word

KubeVirt extends the API with new resource types:

```bash
kubectl get kubevirt -A
kubectl api-resources --api-group=kubevirt.io
```

| Object | Think of it as |
|---|---|
| `VirtualMachine` (VM) | The definition: CPU, memory, disks, NICs, and whether it should be running. Like a Deployment. |
| `VirtualMachineInstance` (VMI) | The VM that is running right now. Like a Pod. |
| `virt-launcher` Pod | The Pod that holds the QEMU process for one VMI. |
| `DataVolume` | A disk image imported or cloned into a PVC by CDI. |

The KubeVirt components run as normal Pods too:

```bash
kubectl get pods -n kubevirt
```

`virt-api` and `virt-controller` are the control plane; `virt-handler` runs on every node and talks to libvirt and QEMU there.

## Create a VM with kubectl

The manifest is plain YAML, like any other workload. This is `manifests/01-vm-live.yaml`:

```yaml
apiVersion: kubevirt.io/v1
kind: VirtualMachine
metadata:
  name: vm-live
  namespace: demo-vms
  labels:
    app.kubernetes.io/part-of: txlf-2026
    app.kubernetes.io/component: vm-live
spec:
  runStrategy: Always
  template:
    metadata:
      labels:
        app.kubernetes.io/part-of: txlf-2026
        app.kubernetes.io/component: vm-live
    spec:
      domain:
        cpu:
          cores: 1
          sockets: 1
          threads: 1
        # kubevirt-manager reads cpu cores/sockets/threads and resources.requests.memory
        resources:
          requests:
            memory: 2Gi
        devices:
          disks:
            - name: containerdisk
              disk:
                bus: virtio
            - name: cloudinit
              disk:
                bus: virtio
          interfaces:
            - name: default
              masquerade: {}
      networks:
        - name: default
          pod: {}
      accessCredentials:
        - sshPublicKey:
            source:
              secret:
                secretName: demo-ssh-key
            propagationMethod:
              noCloud: {}
      volumes:
        - name: containerdisk
          containerDisk:
            image: quay.io/containerdisks/fedora:44-1.7
        - name: cloudinit
          cloudInitNoCloud:
            userData: |
              #cloud-config
              hostname: vm-live
              write_files:
                - path: /etc/motd
                  content: |
                    Texas Linux Fest 2026 - created live with kubectl apply
```

| Part | What it does |
|---|---|
| `kind: VirtualMachine`, `runStrategy: Always` | A VM definition that should always be running |
| `domain.cpu`, `resources.requests.memory` | 1 vCPU and 2 GiB of RAM; Kubernetes uses the memory as the Pod request when it schedules the VM |
| `devices.disks` and `volumes` | Two disks: the OS disk from a container image (`containerDisk`) and a small cloud-init disk |
| `interfaces` and `networks` | One NIC on the Pod network with `masquerade`: the VM uses the Pod IP |
| `accessCredentials` | KubeVirt copies your public key from the `demo-ssh-key` Secret into the guest through cloud-init |
| `cloudInitNoCloud.userData` | First-boot configuration: hostname and a login message |

Apply it and watch it start:

```bash
cd ~/txlf/ansible
kubectl apply -f manifests/01-vm-live.yaml
kubectl get vm,vmi -n demo-vms vm-live -w
```

Press Ctrl+C once the VMI is `Running` (about 30 to 60 seconds). Its disk comes from a container image (`containerDisk`), so there was nothing to import.

## Find the Pod and the QEMU process

```bash
kubectl get pod -n demo-vms -l vm.kubevirt.io/name=vm-live -o wide
```

That Pod is the VM. Look inside its `compute` container, where libvirt runs QEMU:

```bash
POD=$(kubectl get pod -n demo-vms -l vm.kubevirt.io/name=vm-live -o name)
kubectl exec -n demo-vms $POD -c compute -- virsh list
```

Kubernetes schedules, restarts and limits this Pod like any other. The scheduler, quotas, RBAC and audit logs you already use for containers now apply to VMs too: one control plane.

## Use cases

| Use case | Why KubeVirt helps |
|---|---|
| Legacy or vendor apps that cannot be containerized | Run them on the same platform as the new apps |
| Gradual modernization | Keep the VM, move pieces to containers one at a time |
| Platform consolidation | One team, one API, one set of tools instead of two stacks |
| Dev and CI environments | VMs on demand from YAML and Git |
| Workloads needing their own kernel | Kernel modules, other OSes, Windows guests |

## Checkpoint

You created a VM with `kubectl apply` and found its Pod and its QEMU process. Next: what you do with a VM every day.
