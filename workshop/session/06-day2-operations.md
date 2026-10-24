# Module 6: Day-2 operations

**Time:** 20 minutes
**Goal:** Do the things you do every week with VMs: patch a node without downtime, back up and restore, watch metrics and troubleshoot. All with Kubernetes tools.

Keep the `vm-web` page from Module 1 open where you can see it.

## Live migration: move a running VM

`vm-web` runs nginx inside a Fedora VM. The page asks the cluster every 2 seconds which node runs the VM.

```bash
kubectl get vmi -n demo-vms vm-web -o wide
```

Write down the `NODENAME`. Now move the running VM:

```bash
virtctl migrate vm-web -n demo-vms
kubectl get vmim -n demo-vms -w
```

Watch the browser: the page shows "Live migration in progress", then the new node name flashes in orange. The page never reloads and nginx keeps answering. Press Ctrl+C when the migration shows `Succeeded`.

From the UI, the **»** (**Live Migrate**) button on the `vm-web` page in kubevirt-manager does the same.

What happened:

1. KubeVirt started a second `virt-launcher` Pod on another node.
2. QEMU copied the guest memory to it while the VM kept running, then switched over in milliseconds.
3. The disk did not move: it is a Block/RWX volume, so both nodes could open it.
4. The Service followed the new Pod, so the URL kept working.

## Node maintenance

When a node needs patching, you do not move VMs by hand. The VM spec says what to do when its node is drained:

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

Ctrl+C after the node changes, then always undo the cordon:

```bash
kubectl uncordon $NODE
```

With `kubectl drain`, every VM with `evictionStrategy: LiveMigrate` migrates the same way, and the containers on the node are rescheduled as usual. One maintenance procedure for both.

## Backup and restore with snapshots

Use `vm-clone-live`, the VM you created in Module 4 with your SSH key. Put some "important data" in it:

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

Restore. A VM must be stopped to restore its disks:

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

## Metrics

KubeVirt publishes Prometheus metrics for every VM, and OpenShift monitoring collects them next to the container metrics.

In the OpenShift console:

1. In the left menu, click **Observe**, then **Metrics**.
2. Paste a query in the expression box and click **Run queries**:

```text
rate(kubevirt_vmi_vcpu_seconds_total{namespace="demo-vms"}[2m])
```

```text
kubevirt_vmi_memory_domain_bytes{namespace="demo-vms"}
```

![Observe, Metrics in the OpenShift console with a KubeVirt query](../assets/screenshots/console-metrics.png)

In kubevirt-manager the same metrics are drawn per VM:

1. **Virtual Machines**, click **vm-web**.
2. Click the **Monitoring** tab: CPU, memory, network and storage graphs for the last hour.

![The Monitoring tab of vm-web in kubevirt-manager](../assets/screenshots/kvm-monitoring.png)

## Troubleshooting

The evidence is where it is for any Pod:

```bash
kubectl get events -n demo-vms --sort-by=.lastTimestamp | tail
kubectl describe vmi -n demo-vms vm-web | sed -n '/Conditions/,/Events/p'
```

| Symptom | Look at | Usual cause |
|---|---|---|
| VMI stuck in `Scheduling` | `kubectl describe vmi`, events | No node with free CPU/RAM or `/dev/kvm`, a node selector |
| DataVolume import stuck | `kubectl get dv`, importer Pod logs | Image URL, proxy or TLS |
| VM `Running` but app down | Service endpoints, guest console | Guest service, cloud-init not finished |
| Migration fails | `LiveMigratable` condition, migration events | Disk not RWX, CPU model differs between nodes |

## Checkpoint

You moved a running VM with no downtime, used node maintenance rules, restored a VM from a snapshot, and found its metrics and events. Next: the honest trade-offs.
