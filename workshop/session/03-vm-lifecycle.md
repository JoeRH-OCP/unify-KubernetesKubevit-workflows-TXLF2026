# Module 3: VM lifecycle

**Time:** 10 minutes
**Goal:** Log in to a VM, use its console, and stop, start and restart it with the same Kubernetes tools.

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

No SSH? Every VM also has a serial console, even before its network is up:

```bash
virtctl console vm-quick -n demo-vms
```

The console shows the TXLF banner from `/etc/issue`. Exit with Ctrl+]. A graphical console (VNC) is also available; kubevirt-manager shows it in the browser under **Console**.

## Stop, start, restart

```bash
virtctl stop vm-live -n demo-vms
kubectl get vm,vmi,pod -n demo-vms | grep vm-live
```

Stopping removes the VMI and its Pod; the VM object stays, with its definition and disks. Like scaling a Deployment to zero.

```bash
virtctl start vm-live -n demo-vms
kubectl get vmi -n demo-vms vm-live -w
```

Ctrl+C when it is `Running`. To reboot it:

```bash
virtctl restart vm-live -n demo-vms
```

## Who decides if a VM runs: runStrategy

```bash
kubectl get vm -n demo-vms -o 'custom-columns=NAME:.metadata.name,STRATEGY:.spec.runStrategy,STATUS:.status.printableStatus'
```

| runStrategy | Behavior |
|---|---|
| `Always` | Keep it running; restart it if it stops or its node fails |
| `Halted` | Keep it stopped |
| `Manual` | You start and stop it; nothing restarts it for you |
| `RerunOnFailure` | Restart only if it fails |

`virtctl start` and `virtctl stop` just change this field. That is the Kubernetes way: you declare the state, a controller makes it happen.

## The same in the UI

Open kubevirt-manager, **Virtual Machines**, pick `vm-live`: the buttons at the top (pause, start, stop, restart) call the same API. In the **Details**, **Networking** and **Disks** tabs you see what the YAML declared.

## Checkpoint

You logged in with SSH and the serial console, and controlled the VM with `virtctl` and `runStrategy`. Next: where its disks live.
