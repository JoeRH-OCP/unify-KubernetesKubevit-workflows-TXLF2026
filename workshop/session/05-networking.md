# Module 5: Networking (VMs and containers on the same network)

**Time:** 12 minutes
**Goal:** See that a VM sits on the Pod network, is reached through a normal Service, and talks to containers by DNS name.

## A VM on the Pod network

```bash
kubectl get vmi -n demo-vms vm-web -o jsonpath='{.status.interfaces[0].ipAddress}{"\n"}'
kubectl get pod -n demo-vms -l vm.kubevirt.io/name=vm-web -o wide
```

The VM's address is the Pod's address. The VM uses the `masquerade` binding: from the outside it looks like any Pod, so the cluster network, DNS and NetworkPolicy apply to it unchanged.

## A Service in front of a VM

`vm-web` is reachable from your browser through two standard Kubernetes objects:

```bash
kubectl get svc,ingress -n demo-vms vm-web
kubectl get svc -n demo-vms vm-web -o jsonpath='{.spec.selector}{"\n"}'
```

The Service selects Pods with the label `vm.kubevirt.io/name: vm-web`. Every `virt-launcher` Pod of that VM carries the label, so the Service keeps working when the VM restarts or moves.

## A container talks to a VM

Start a throwaway container and call the VM by its Service name, like any microservice:

```bash
kubectl run curl -n demo-vms --rm -it --restart=Never --image=quay.io/curl/curl:latest -- curl -s -o /dev/null -w '%{http_code}\n' http://vm-web.demo-vms.svc/
```

`200`: nginx inside the VM answered a container.

The landing page in your browser mixes both worlds behind one URL: `/` goes to the VM (`vm-web` Service) and `/api` goes to `node-reporter`, a container that reads the VM's status from the Kubernetes API:

```bash
kubectl get ingress -n demo-vms vm-web -o jsonpath='{range .spec.rules[0].http.paths[*]}{.path} -> {.backend.service.name}{"\n"}{end}'
kubectl run curl -n demo-vms --rm -it --restart=Never --image=quay.io/curl/curl:latest -- curl -s 'http://node-reporter.demo-vms.svc:8080/api/node?vm=vm-web'
```

## Expose any port of a VM

Create a Service for SSH on your own VM with one command:

```bash
virtctl expose vm vm-live -n demo-vms --name vm-live-ssh --port 22 --type ClusterIP
kubectl get svc,endpoints -n demo-vms vm-live-ssh
```

Any Pod in the cluster now reaches `vm-live-ssh.demo-vms.svc:22`.

## More than one network

Some VMs need to sit on an existing VLAN or data center network as well. KubeVirt supports secondary interfaces through Multus: a `NetworkAttachmentDefinition` plus a Linux bridge set up on the nodes (for example with the NMState operator). The VM then has one NIC on the Pod network and another one directly on the physical network. See `ansible/manifests/06-vm-secondary-net.yaml` for an example; it is not enabled on the workshop clusters.

## Checkpoint

A VM gets a Pod IP, sits behind Services and Ingress, and talks to containers by DNS name. Next: running all this day after day.
