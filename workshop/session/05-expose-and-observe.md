# Module 5: Expose and observe VMs like any app

**Time:** 15 minutes
**Goal:** See that a VM is exposed with a normal Service and Ingress, and that it is monitored with the same metrics stack as containers.

## Networking: a Service in front of a VM

`vm-web` is reachable from your browser through two standard Kubernetes objects. Look at them:

```bash
kubectl get svc,ingress -n demo-vms vm-web
kubectl get svc -n demo-vms vm-web -o jsonpath='{.spec.selector}{"\n"}'
```

The Service selects Pods with the label `vm.kubevirt.io/name: vm-web`. Every `virt-launcher` Pod of that VM has the label, which is why the URL kept working after the migration. The VM uses the Pod network with `masquerade`: it gets the Pod's IP from the outside, like a container.

Expose your own `vm-live` the same way, with SSH this time:

```bash
virtctl expose vm vm-live -n demo-vms --name vm-live-ssh --port 22 --type ClusterIP
kubectl get svc,endpoints -n demo-vms vm-live-ssh
```

From any Pod in the cluster, `vm-live-ssh.demo-vms.svc:22` now reaches the VM. Same DNS, same Services, same NetworkPolicy as any app.

## Observe: metrics you already know how to use

KubeVirt publishes Prometheus metrics for every VM, and OpenShift monitoring collects them. In the console, open **Observe, Metrics** and run:

```text
rate(kubevirt_vmi_vcpu_seconds_total{namespace="demo-vms"}[2m])
```

```text
kubevirt_vmi_memory_domain_bytes{namespace="demo-vms"}
```

```text
rate(kubevirt_vmi_network_receive_bytes_total{namespace="demo-vms",name="vm-web"}[2m])
```

kubevirt-manager draws the same metrics per VM. Open `vm-web` there and look at the graphs, the **Networking** tab (NIC, IP) and **Overview** (guest OS from the guest agent).

## Troubleshoot: events and conditions

When something is wrong, the evidence is where it is for any Pod:

```bash
kubectl get events -n demo-vms --sort-by=.lastTimestamp | tail
kubectl describe vmi -n demo-vms vm-web | sed -n '/Conditions/,/Events/p'
```

Useful conditions: `Ready`, `AgentConnected` (guest agent), and `LiveMigratable`. If a VM cannot migrate, `LiveMigratable` says why (for example, a disk that is not RWX).

| Symptom | Look at | Usual cause |
|---|---|---|
| VMI stuck in `Scheduling` | `kubectl describe vmi`, events | No node with free CPU/RAM or `/dev/kvm`, a node selector |
| DataVolume import stuck | `kubectl get dv`, importer Pod logs | Image URL, proxy or TLS |
| VM `Running` but app down | Service endpoints, guest console | Guest service, cloud-init not finished |
| Migration fails | `LiveMigratable`, migration events | Disk not RWX, CPU model differs between nodes |

## Checkpoint

A VM uses Services, Ingress, DNS, Prometheus and events like any Pod. Next: recap and where to go from here.
