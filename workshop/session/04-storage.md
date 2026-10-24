# Module 4: Storage (disks are PVCs)

**Time:** 15 minutes
**Goal:** See how VM disks map to Kubernetes storage, and create a new VM from a golden image with a storage-level clone.

## The golden image

When the instructor prepared your cluster, CDI (the Containerized Data Importer) imported the Fedora 44 cloud image from `download.fedoraproject.org` into a PVC:

```bash
kubectl get dv,pvc -n demo-vms golden-image
kubectl get dv -n demo-vms golden-image -o jsonpath='{.spec.source.http.url}{"\n"}'
```

The same mechanism imports from container registries, S3, or an upload from your laptop. It is also how existing VM disks from other platforms come in.

Look at how the disk is stored:

```bash
kubectl get pvc -n demo-vms golden-image -o 'custom-columns=NAME:.metadata.name,MODE:.spec.volumeMode,ACCESS:.spec.accessModes,CLASS:.spec.storageClassName'
```

- **Block:** the VM gets a raw block device, no filesystem in between.
- **ReadWriteMany (RWX):** two nodes can open the disk at the same time. That is what makes live migration possible in Module 6.
- **StorageClass:** Ceph RBD from OpenShift Data Foundation here; any CSI driver with these features works.

## How CDI clones

```bash
kubectl get storageprofile ocs-external-storagecluster-ceph-rbd -o jsonpath='{.status}{"\n"}'
```

`cloneStrategy: snapshot` means CDI clones by taking a CSI snapshot of the source and restoring it. No data is copied through the network.

## Clone a new VM

This is `manifests/02-vm-clone-live.yaml`. It is the same kind of VM, but its disk is a clone of `golden-image`:

```yaml
apiVersion: kubevirt.io/v1
kind: VirtualMachine
metadata:
  name: vm-clone-live
  namespace: demo-vms
  labels:
    app.kubernetes.io/part-of: txlf-2026
    app.kubernetes.io/component: clone
spec:
  runStrategy: Always
  dataVolumeTemplates:
    - metadata:
        name: vm-clone-live-rootdisk
        labels:
          app.kubernetes.io/part-of: txlf-2026
      spec:
        source:
          pvc:
            namespace: demo-vms
            name: golden-image
        storage:
          storageClassName: ocs-external-storagecluster-ceph-rbd
          volumeMode: Block
          accessModes:
            - ReadWriteMany
          resources:
            requests:
              storage: 10Gi
  template:
    metadata:
      labels:
        app.kubernetes.io/part-of: txlf-2026
        app.kubernetes.io/component: clone
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
            - name: rootdisk
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
      evictionStrategy: LiveMigrate
      accessCredentials:
        - sshPublicKey:
            source:
              secret:
                secretName: demo-ssh-key
            propagationMethod:
              noCloud: {}
      volumes:
        - name: rootdisk
          dataVolume:
            name: vm-clone-live-rootdisk
        - name: cloudinit
          cloudInitNoCloud:
            userData: |
              #cloud-config
              hostname: vm-clone-live
```

| Part | What it does |
|---|---|
| `dataVolumeTemplates` | Creates the VM's own disk, `vm-clone-live-rootdisk`, by cloning the `golden-image` PVC |
| `storage` | Explicit StorageClass, `Block` mode, `ReadWriteMany`, 10Gi (at least the size of the source) |
| `volumes.dataVolume` | The VM boots from that cloned disk |
| `evictionStrategy: LiveMigrate` | If its node is drained, the VM migrates instead of stopping (Module 6) |
| `accessCredentials`, `cloudInitNoCloud` | Same as `vm-live`: your SSH key and a hostname |

Apply it and watch the clone:

```bash
cd ~/txlf/ansible
kubectl apply -f manifests/02-vm-clone-live.yaml
kubectl get dv -n demo-vms vm-clone-live-rootdisk -w
```

Ctrl+C when the DataVolume shows `Succeeded`. A 10 GiB disk should be ready in seconds. Then:

```bash
kubectl get vmi -n demo-vms vm-clone-live
kubectl get volumesnapshot -n demo-vms
```

The VolumeSnapshot is what CDI used to make the clone.

## Every VM disk you have

```bash
kubectl get pvc -n demo-vms
```

`vm-web`, `vm-clone-1` to `vm-clone-3` and your new `vm-clone-live` all started from `golden-image`. See it in kubevirt-manager:

1. Left menu, **Virtual Machines**, then click **vm-clone-live**.
2. Click the **Disks** tab. The `rootdisk` row shows the DataVolume, its size, access mode, StorageClass and the source `pvc (demo-vms - golden-image)`.

![The Disks tab of vm-clone-live in kubevirt-manager](../assets/screenshots/kvm-disks.png)

## Checkpoint

A VM disk is a PVC. Importing an image and cloning a VM are Kubernetes storage operations done with CSI. Next: how VMs and containers talk to each other.
