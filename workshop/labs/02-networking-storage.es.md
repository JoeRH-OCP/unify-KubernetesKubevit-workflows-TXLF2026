# Laboratorio 2: Redes y almacenamiento de Kubernetes

**Tiempo sugerido:** 3–4 horas  
**Objetivo:** seguir el tráfico a través de un Service, observar políticas de red y comprobar que un PVC sobrevive al reemplazo de un Pod.

## Parte A: Redes

Cada Pod recibe su propia IP en el cluster; el plugin CNI conecta los nodos. Los Services dan una dirección estable a Pods que aparecen y desaparecen.

| Exposición | Uso |
|---|---|
| ClusterIP | Tráfico dentro del cluster |
| NodePort | Un puerto abierto en cada nodo |
| LoadBalancer | Un balanceador externo, si el entorno lo tiene |
| Ingress o Route | Entrada HTTP/HTTPS con ruteo por host o ruta |

NetworkPolicy controla el tráfico hacia y desde los Pods, si el CNI la aplica.

Usa el Deployment y Service `web` del Laboratorio 1.

### Descubrimiento y acceso a Services

```bash
kubectl -n workshop-basics get pods -o wide
kubectl -n workshop-basics get endpoints web
kubectl -n workshop-basics run client --image=registry.access.redhat.com/ubi9/ubi-minimal:latest --restart=Never -- sleep 3600
kubectl -n workshop-basics exec client -- curl -sS http://web:8080
```

Repasa el modelo de red de Pods, responsabilidades del CNI y descubrimiento de ClusterIP. Compara NodePort y LoadBalancer. En OpenShift, contrasta Ingress con Route.

### Ejercicio de NetworkPolicy

Primero confirma que el CNI aplica políticas. Crea una NetworkPolicy que seleccione `app: web` y permita ingreso solo desde Pods con etiqueta `access: allowed` dentro del mismo namespace, en TCP 8080. Aplica la política, agrega la etiqueta al Pod cliente y comprueba el acceso antes y después.

**Checkpoint:** explica por qué una política no tiene efecto si el plugin de red no la implementa.

## Parte B: Almacenamiento persistente

El almacenamiento efímero termina con el Pod. Para conservar datos, un PVC pide almacenamiento; se enlaza a un PV, normalmente aprovisionado al momento por una StorageClass. Revisa el modo de acceso (ReadWriteOnce, ReadWriteMany, ReadOnlyMany), el tamaño pedido y la política de reclaim (qué pasa con el volumen cuando se borra el claim). Las VMs que hacen live migration necesitan ReadWriteMany.

Crea un PVC con la StorageClass predeterminada (o indica `storageClassName: CHANGEME`). Solicita 1Gi en modo `ReadWriteOnce`. Crea un Pod `storage-writer` que monte el PVC en `/data` y escriba un archivo:

```bash
kubectl apply -f pvc-pod.yaml
kubectl -n workshop-basics wait --for=condition=Ready pod/storage-writer --timeout=180s
kubectl -n workshop-basics exec storage-writer -- cat /data/check.txt
kubectl -n workshop-basics delete pod storage-writer
```

Vuelve a crear solo el Pod usando el mismo claim y verifica que `/data/check.txt` permanezca.

**Checkpoint:** compara almacenamiento efímero con el respaldado por PVC. Revisa el provisioner, estado del claim, modo de acceso y política de reclaim de la StorageClass.

## Limpieza

Elimina el namespace al terminar. Si lo conservarás para el próximo laboratorio, elimina solo el cliente y los recursos de almacenamiento.
