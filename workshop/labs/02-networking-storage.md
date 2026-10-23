# Lab 2 — Kubernetes networking and storage

**Suggested time:** 3–4 hours across Modules 3 and 4  
**Goal:** Trace traffic through a Service, observe policy behavior, and prove that a PVC survives Pod replacement.

## Part A — Networking

Use the `web` Deployment and Service from Lab 1.

### Service discovery and access

```bash
kubectl -n workshop-basics get pods -o wide
kubectl -n workshop-basics get endpoints web
kubectl -n workshop-basics run client --image=registry.access.redhat.com/ubi9/ubi-minimal:latest --restart=Never -- sleep 3600
kubectl -n workshop-basics exec client -- curl -sS http://web:8080
```

Discuss the Pod network model, CNI responsibilities, ClusterIP service discovery, and how NodePort/LoadBalancer differ. On OpenShift, compare an Ingress with a Route.

### NetworkPolicy exercise

Create a policy that selects `app: web` and allows ingress only from Pods labeled `access: allowed` in the same namespace. Participants should first verify that their CNI enforces NetworkPolicy.

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: web-allow-labeled-clients
  namespace: workshop-basics
spec:
  podSelector:
    matchLabels:
      app: web
  policyTypes:
    - Ingress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              access: allowed
      ports:
        - protocol: TCP
          port: 8080
```

Apply it, add the label to the client Pod, and compare access before and after:

```bash
kubectl apply -f network-policy.yaml
kubectl -n workshop-basics label pod client access=allowed
kubectl -n workshop-basics exec client -- curl -m 3 -sS http://web:8080
```

**Checkpoint:** Explain why a policy may have no effect on a cluster whose network plugin does not enforce it.

## Part B — Persistent storage

Create a PVC using the cluster's default StorageClass. If there is no default class, add `storageClassName: CHANGEME` to the claim.

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: workshop-data
  namespace: workshop-basics
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
---
apiVersion: v1
kind: Pod
metadata:
  name: storage-writer
  namespace: workshop-basics
spec:
  containers:
    - name: writer
      image: registry.access.redhat.com/ubi9/ubi-minimal:latest
      command: ["/bin/sh", "-c", "echo 'data survives pod replacement' > /data/check.txt; sleep 36000"]
      volumeMounts:
        - name: data
          mountPath: /data
  volumes:
    - name: data
      persistentVolumeClaim:
        claimName: workshop-data
```

Apply and test:

```bash
kubectl apply -f pvc-pod.yaml
kubectl -n workshop-basics wait --for=condition=Ready pod/storage-writer --timeout=180s
kubectl -n workshop-basics exec storage-writer -- cat /data/check.txt
kubectl -n workshop-basics delete pod storage-writer
```

Reapply only the Pod portion with the same claim, then verify `/data/check.txt` remains.

**Checkpoint:** Compare ephemeral container storage with PVC-backed storage. Review the StorageClass provisioner, PVC status, access mode, and reclaim policy.

## Cleanup

Delete the namespace after all checks. If keeping the namespace for the next lab, remove only the client and storage resources.
