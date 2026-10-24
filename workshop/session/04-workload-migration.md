# Module 4: Unified workload migration

**Time:** 30 minutes
**Goal:** Move a running VM between nodes with no downtime, protect it with a snapshot, bring it back after a mistake, and see how existing VMs migrate into Kubernetes.

Keep the `vm-web` page from Module 1 open where you can see it.

## Part A: live migration (10 minutes)

`vm-web` runs nginx inside a Fedora VM. The page asks the cluster every 2 seconds which node runs the VM.

```bash
kubectl get vmi -n demo-vms vm-web -o wide
```

Write down the `NODENAME`. Now move the running VM:

```bash
virtctl migrate vm-web -n demo-vms
kubectl get vmim -n demo-vms -w
```

Watch the browser while the migration runs: the page shows "Live migration in progress", then the new node name flashes in orange. The page never reloads and nginx keeps answering.

Press Ctrl+C when the migration shows `Succeeded`, then confirm:

```bash
kubectl get vmi -n demo-vms vm-web -o wide
```

What happened under the hood:

1. KubeVirt started a second `virt-launcher` Pod on another node.
2. QEMU copied the guest memory to it while the VM kept running, then switched over in milliseconds.
3. The disk did not move: it is a Block/RWX volume, so both nodes could open it.
4. The Kubernetes Service follows the new Pod, so the URL keeps working.

```bash
kubectl get pods -n demo-vms -l vm.kubevirt.io/name=vm-web -o wide
```

The old Pod is `Completed`; the new one is `Running`.

## Part B: node maintenance moves VMs for you (5 minutes)

When a node needs patching, you do not migrate VMs by hand. The VM spec says what to do when its node is drained:

```bash
kubectl get vm vm-web -n demo-vms -o jsonpath='{.spec.template.spec.evictionStrategy}{"\n"}'
```

`LiveMigrate` means "if my node is drained, migrate me, don't kill me". Try it safely with a cordon:

```bash
NODE=$(kubectl get vmi -n demo-vms vm-web -o jsonpath='{.status.nodeName}')
kubectl cordon $NODE
virtctl migrate vm-web -n demo-vms
kubectl get vmi -n demo-vms vm-web -o wide -w
```

Ctrl+C after the node changes. The cordoned node accepts no new Pods, so the VM went to another node. Always undo the cordon:

```bash
kubectl uncordon $NODE
```

With `kubectl drain`, every VM with `evictionStrategy: LiveMigrate` on that node would migrate the same way. The rest of the Pods on the node are rescheduled as usual. One set of rules for containers and VMs.

## Part C: snapshot, break, restore (10 minutes)

Use `vm-clone-live`, the VM you created in Module 3 with your SSH key. First, put some "important data" in it:

```bash
virtctl ssh fedora@vm/vm-clone-live -n demo-vms -c 'echo "TXLF 2026 important data" | sudo tee /srv/data.txt'
```

Take a snapshot of the running VM:

```bash
kubectl apply -f - <<'EOF'
apiVersion: snapshot.kubevirt.io/v1beta1
kind: VirtualMachineSnapshot
metadata:
  name: before-oops
  namespace: demo-vms
spec:
  source:
    apiGroup: kubevirt.io
    kind: VirtualMachine
    name: vm-clone-live
EOF
kubectl get vmsnapshot -n demo-vms before-oops -w
```

Ctrl+C when `READYTOUSE` is `true`. The QEMU guest agent froze the guest filesystems so the snapshot is consistent, and Ceph took a CSI snapshot of the disk.

Now the mistake:

```bash
virtctl ssh fedora@vm/vm-clone-live -n demo-vms -c 'sudo rm -f /srv/data.txt; ls -l /srv'
```

The file is gone. Restore the VM. It must be stopped to restore its disks:

```bash
virtctl stop vm-clone-live -n demo-vms
kubectl wait vmi/vm-clone-live -n demo-vms --for=delete --timeout=120s
kubectl apply -f - <<'EOF'
apiVersion: snapshot.kubevirt.io/v1beta1
kind: VirtualMachineRestore
metadata:
  name: undo-oops
  namespace: demo-vms
spec:
  target:
    apiGroup: kubevirt.io
    kind: VirtualMachine
    name: vm-clone-live
  virtualMachineSnapshotName: before-oops
EOF
kubectl get vmrestore -n demo-vms undo-oops -w
```

Ctrl+C when `COMPLETE` is `true`, then start the VM and check the file:

```bash
virtctl start vm-clone-live -n demo-vms
kubectl wait vmi/vm-clone-live -n demo-vms --for=condition=AgentConnected --timeout=180s
virtctl ssh fedora@vm/vm-clone-live -n demo-vms -c 'cat /srv/data.txt'
```

The data is back, exactly as it was when you took the snapshot.

> The instructor shows the same flow on `vm-web` with the web page: break the site, restore, and watch it come back (`ansible/manifests/04-snapshot.yaml` and `05-restore.yaml`).

## Part D: migrating VMs into Kubernetes (5 minutes, discussion)

So far the VMs were born in the cluster. Most organizations start with VMs on another hypervisor. Three ways to bring them in:

| Path | What it does | Good for |
|---|---|---|
| Disk import with CDI | A `DataVolume` imports a qcow2/raw image from HTTP, S3, a registry or an upload (this is how `golden-image` was made) | Single VMs, golden images, appliances |
| Migration Toolkit for Virtualization (Forklift) | Plans and runs migrations from VMware vSphere, oVirt/RHV, OpenStack or OVA, converts drivers and maps networks/storage | Fleets of VMs, cutover windows |
| Rebuild as containers | Move the app out of the VM when it makes sense | Stateless services, new versions |

The point of "unified": once a VM is inside, it is scheduled, networked, stored, monitored, migrated and backed up with the same Kubernetes tools as your containers. You can move each workload to a container later, one at a time, or never.

## Checkpoint

You live-migrated a VM with no downtime, used node maintenance rules, restored a VM from a snapshot, and know the paths to bring VMs into the cluster.
