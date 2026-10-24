# Module 3: Disks are PVCs (and clones take seconds)

**Time:** 15 minutes
**Goal:** See how VM disks map to Kubernetes storage, and create a new VM from a golden image with a storage-level clone.

## The golden image

When the instructor prepared your cluster, CDI imported the Fedora 44 cloud image from `download.fedoraproject.org` into a PVC:

```bash
kubectl get dv,pvc -n demo-vms golden-image
kubectl get dv -n demo-vms golden-image -o jsonpath='{.spec.source.http.url}{"\n"}'
```

That import is the simplest form of workload migration: an existing disk image from outside the cluster becomes a Kubernetes volume. The same mechanism imports from registries, S3 or an upload from your laptop.

Look at how the disk is stored:

```bash
kubectl get pvc -n demo-vms golden-image -o custom-columns=NAME:.metadata.name,MODE:.spec.volumeMode,ACCESS:.spec.accessModes,CLASS:.spec.storageClassName
```

- **Block:** the VM gets a raw block device, no filesystem in between.
- **ReadWriteMany (RWX):** two nodes can open the disk at the same time. That is what makes live migration possible in Module 4.
- **StorageClass:** Ceph RBD from OpenShift Data Foundation; any CSI driver with these features works.

## How CDI clones

```bash
kubectl get storageprofile ocs-external-storagecluster-ceph-rbd -o jsonpath='{.status}{"\n"}'
```

`cloneStrategy: snapshot` means CDI clones by taking a CSI snapshot of the source and restoring it. No data is copied through the network.

## Clone a new VM

```bash
cat manifests/02-vm-clone-live.yaml
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

`vm-web`, `vm-clone-1` to `vm-clone-3` and your new `vm-clone-live` all started from `golden-image`. In kubevirt-manager, open **Virtual Machines**, pick `vm-clone-live` and look at the **Disks** tab: the source is `pvc (demo-vms - golden-image)`.

## Checkpoint

A VM disk is a PVC. Importing an image and cloning a VM are Kubernetes storage operations, done with CSI snapshots. Next: moving a running VM without stopping it.
