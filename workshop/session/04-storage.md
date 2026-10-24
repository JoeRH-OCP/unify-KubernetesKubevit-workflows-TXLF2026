# Module 4: Storage (disks are PVCs)

**Time:** 12 minutes
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
kubectl get pvc -n demo-vms golden-image -o custom-columns=NAME:.metadata.name,MODE:.spec.volumeMode,ACCESS:.spec.accessModes,CLASS:.spec.storageClassName
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

```bash
cd ~/txlf/ansible
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

`vm-web`, `vm-clone-1` to `vm-clone-3` and your new `vm-clone-live` all started from `golden-image`. In kubevirt-manager, open `vm-clone-live` and look at the **Disks** tab: the source is `pvc (demo-vms - golden-image)`.

## Checkpoint

A VM disk is a PVC. Importing an image and cloning a VM are Kubernetes storage operations done with CSI. Next: how VMs and containers talk to each other.
