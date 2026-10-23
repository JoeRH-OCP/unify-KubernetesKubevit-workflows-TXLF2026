# Lab 1 — Container and Kubernetes foundations

**Suggested time:** 3.5–4.5 hours across Modules 1 and 2  
**Goal:** Build and run an OCI image, then deploy and expose a small application on Kubernetes.

## Part A — Container lifecycle

### Concepts

- A container is an isolated process using the host kernel; a VM runs a guest OS with a virtual hardware boundary.
- OCI images are layered, content-addressed artifacts stored in registries.
- CRI-O and containerd are Kubernetes node runtimes. Podman and Docker are common developer tools.
- Container lifecycle: build/pull, create, start, inspect/log, stop, remove, push.

### Build and run

Create a directory and save this as `Containerfile`:

```Dockerfile
FROM registry.access.redhat.com/ubi9/ubi-minimal:latest
RUN microdnf install -y nginx && microdnf clean all
RUN printf 'Hello from the workshop container\n' > /usr/share/nginx/html/index.html
EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
```

Build and inspect it with Podman:

```bash
podman build -t workshop-web:v1 .
podman image inspect workshop-web:v1
podman run -d --name workshop-web -p 8080:8080 workshop-web:v1
podman ps
curl http://localhost:8080
podman logs workshop-web
podman stop workshop-web
podman rm workshop-web
```

If the base image's nginx listens on port 80, change `EXPOSE` and publish mapping to 80. Confirm the port from the image or container before troubleshooting.

**Checkpoint:** Explain which parts are in the image and which state is created at runtime. Identify the image layers and container process.

### Optional registry push

Set your own registry and authenticate. Do not commit credentials.

```bash
export IMAGE=CHANGEME
podman tag workshop-web:v1 "$IMAGE"
podman login CHANGEME_REGISTRY
podman push "$IMAGE"
```

## Part B — Kubernetes objects

### Inspect the cluster

```bash
kubectl config current-context
kubectl get nodes -o wide
kubectl get namespaces
kubectl explain deployment.spec
```

Discuss control plane responsibilities, worker nodes, Pods, controllers, Services, and declarative reconciliation.

### Deploy a multi-container Pod

Create a namespace and save as `multi-container.yaml`:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: workshop-basics
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: web-content
  namespace: workshop-basics
data:
  index.html: |
    <h1>Workshop web</h1>
    <p>Served by nginx in Kubernetes.</p>
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
  namespace: workshop-basics
spec:
  replicas: 1
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
        - name: nginx
          image: registry.access.redhat.com/ubi9/nginx-124:latest
          ports:
            - name: http
              containerPort: 8080
          volumeMounts:
            - name: content
              mountPath: /usr/share/nginx/html
        - name: heartbeat
          image: busybox:1.36
          command: ["sh", "-c", "while true; do date >> /shared/heartbeat.log; sleep 30; done"]
          volumeMounts:
            - name: shared
              mountPath: /shared
      volumes:
        - name: content
          configMap:
            name: web-content
        - name: shared
          emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: web
  namespace: workshop-basics
spec:
  selector:
    app: web
  ports:
    - name: http
      port: 8080
      targetPort: http
```

Apply and validate:

```bash
kubectl apply -f multi-container.yaml
kubectl -n workshop-basics rollout status deployment/web
kubectl -n workshop-basics get pods,svc
kubectl -n workshop-basics port-forward service/web 8080:8080
```

In a second terminal, run `curl http://localhost:8080`. Inspect both containers with `kubectl -n workshop-basics get pod` and `kubectl -n workshop-basics exec deploy/web -c heartbeat -- tail /shared/heartbeat.log`. The heartbeat sidecar writes to a shared `emptyDir` volume; the ConfigMap provides the web page.

**Checkpoint:** Change the ConfigMap and observe how the mounted file changes. Scale the Deployment to two replicas. Explain why a Service provides a stable endpoint when Pod IPs change.

## Cleanup

```bash
kubectl delete namespace workshop-basics
```
