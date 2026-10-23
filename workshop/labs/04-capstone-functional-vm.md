# Lab 4 — Capstone: deploy a functional Linux VM

**Suggested time:** 90–120 minutes  
**Success condition:** A persistent Linux VM reaches Running, cloud-init installs and starts an HTTP server, a Kubernetes Service selects the VM, and `curl` returns the expected page.

This lab is the workshop's final exercise. It combines CDI image import, PVC-backed VM storage, cloud-init, KubeVirt lifecycle, and Kubernetes networking.

## Before you start

- KubeVirt or OpenShift Virtualization is healthy.
- CDI is installed and healthy.
- The namespace has permission to create VMs, DataVolumes, PVCs, and Services.
- A default StorageClass exists, or you know its name.
- Choose a trusted Fedora Cloud qcow2 URL that is reachable by the cluster and supports cloud-init. Replace the manifest's `CHANGEME_IMAGE_URL`.
- Replace `CHANGEME_SSH_PUBLIC_KEY` with a public SSH key if SSH access is desired. The Service intentionally exposes HTTP only; console access remains available through `virtctl`.
- Confirm your image's cloud-init datasource and package manager. This template targets Fedora cloud images with cloud-init and the `httpd` package.

## Deploy

Review [the manifest](../manifests/capstone-functional-vm.yaml), replace all placeholders, then apply it:

```bash
kubectl apply -f workshop/manifests/capstone-functional-vm.yaml
kubectl -n kubevirt-workshop get datavolume,pvc,vm,vmi,svc
kubectl -n kubevirt-workshop wait --for=condition=Ready pvc/final-vm-disk --timeout=20m
kubectl -n kubevirt-workshop wait --for=condition=Ready vmi/final-functional-vm --timeout=10m
```

DataVolume import can take several minutes. Inspect progress with:

```bash
kubectl -n kubevirt-workshop describe datavolume final-vm-disk
kubectl -n kubevirt-workshop get pods
```

The VM starts automatically. If it does not:

```bash
virtctl start final-functional-vm -n kubevirt-workshop
```

## Validate guest initialization and HTTP

Check the guest console and cloud-init output:

```bash
virtctl console final-functional-vm -n kubevirt-workshop
```

Exit the console with the documented escape sequence shown by virtctl (commonly Ctrl+]).

Forward the Service to the workstation:

```bash
kubectl -n kubevirt-workshop port-forward service/final-vm-web 8080:80
```

From another terminal:

```bash
curl --fail http://127.0.0.1:8080/
```

Expected response includes: `KubeVirt capstone is working`.

A successful result proves that the image imported, the VM booted, cloud-init ran, the guest HTTP service started, the VM network is reachable through the Service, and the port-forward path works.

## Investigate if the check fails

```bash
kubectl -n kubevirt-workshop get vm,vmi,datavolume,pvc,pods,svc -o wide
kubectl -n kubevirt-workshop describe vmi final-functional-vm
kubectl -n kubevirt-workshop describe datavolume final-vm-disk
kubectl -n kubevirt-workshop get events --sort-by=.lastTimestamp
virtctl console final-functional-vm -n kubevirt-workshop
```

Common causes:

- **PVC/DataVolume pending:** StorageClass missing, insufficient capacity, or CDI importer cannot reach the image URL.
- **VM does not schedule:** node lacks exposed virtualization support, resource quota is exhausted, or node selectors/taints prevent scheduling.
- **VM running but page unavailable:** cloud-init has not finished, image lacks cloud-init or `httpd`, or the VM's network/service selector does not match.
- **Port-forward fails:** Service has no endpoints; inspect `kubectl get endpoints final-vm-web -n kubevirt-workshop` and the VMI labels.
- **Image boot failure:** URL does not point to a compatible qcow2 cloud image, or the guest image architecture differs from the cluster nodes.

## Stretch goals

1. Add a second data disk using another DataVolume and mount it in the guest.
2. Change the page content through cloud-init and redeploy with a new VM name.
3. Expose the service through an Ingress or OpenShift Route if the environment supports VM service routing.
4. Add CPU/memory requests and limits, then compare requested resources with actual guest use.
5. Document the GitOps workflow to update the VM template safely.

## Cleanup

Stop and remove the VM resources after the exercise. PVC retention depends on the DataVolume/storage lifecycle policy, so inspect the resources before deleting them.

```bash
kubectl delete -f workshop/manifests/capstone-functional-vm.yaml
kubectl get pvc -n kubevirt-workshop
```

Delete the namespace only after verifying that no participant data must be retained.
