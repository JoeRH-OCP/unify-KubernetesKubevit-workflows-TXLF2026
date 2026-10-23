# Laboratorio 1 — Fundamentos de contenedores y Kubernetes

**Tiempo sugerido:** 3.5–4.5 horas para los módulos 1 y 2  
**Objetivo:** construir y ejecutar una imagen OCI, y después desplegar y exponer una aplicación en Kubernetes.

## Parte A — Ciclo de vida del contenedor

Un contenedor es un proceso aislado que comparte el kernel del host; una VM ejecuta un sistema operativo guest. Las imágenes OCI son artefactos por capas almacenados en registries. CRI-O y containerd son runtimes de nodos Kubernetes; Podman y Docker son herramientas comunes para desarrollo.

Crea un directorio y guarda como `Containerfile`:

```Dockerfile
FROM registry.access.redhat.com/ubi9/ubi-minimal:latest
RUN microdnf install -y nginx && microdnf clean all
RUN printf 'Hello from the workshop container\n' > /usr/share/nginx/html/index.html
EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
```

Construye e inspecciona con Podman:

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

Si nginx escucha en el puerto 80 dentro de la imagen, ajusta `EXPOSE` y el mapeo. Confirma el puerto antes de investigar fallas.

**Checkpoint:** explica qué contenido vive en la imagen y qué estado se crea al ejecutar el contenedor. Identifica sus capas y proceso.

### Push opcional al registry

Configura tu registry y autentícate. No guardes credenciales en Git.

```bash
export IMAGE=CHANGEME
podman tag workshop-web:v1 "$IMAGE"
podman login CHANGEME_REGISTRY
podman push "$IMAGE"
```

## Parte B — Objetos de Kubernetes

Inspecciona el clúster:

```bash
kubectl config current-context
kubectl get nodes -o wide
kubectl get namespaces
kubectl explain deployment.spec
```

Repasa responsabilidades del control plane, worker nodes, Pods, controladores, Services y reconciliación declarativa.

### Desplegar un Pod con varios contenedores

Crea el namespace `workshop-basics` y un archivo YAML con estos recursos:
- ConfigMap `web-content` con un `index.html`.
- Deployment `web` con nginx y un sidecar BusyBox que escribe un heartbeat en un volumen `emptyDir` compartido.
- Un Service `web` en el puerto 8080.

Aplica y valida el manifiesto:

```bash
kubectl apply -f multi-container.yaml
kubectl -n workshop-basics rollout status deployment/web
kubectl -n workshop-basics get pods,svc
kubectl -n workshop-basics port-forward service/web 8080:8080
```

En otra terminal, ejecuta `curl http://localhost:8080`. Consulta los dos contenedores y el archivo de heartbeat con `kubectl exec`.

**Checkpoint:** modifica el ConfigMap, escala el Deployment a dos réplicas y explica cómo el Service mantiene un endpoint estable aunque cambien las IPs de los Pods.

## Limpieza

```bash
kubectl delete namespace workshop-basics
```
