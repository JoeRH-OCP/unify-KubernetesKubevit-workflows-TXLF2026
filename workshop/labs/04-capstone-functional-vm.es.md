# Laboratorio final — Desplegar una VM Linux funcional

**Tiempo sugerido:** 90–120 minutos  
**Condición de éxito:** la VM Linux persistente llega a Running, cloud-init instala e inicia un servidor HTTP, un Service de Kubernetes selecciona la VM y `curl` devuelve la página esperada.

Este ejercicio final combina importación de imagen con CDI, almacenamiento PVC, cloud-init, ciclo de vida de KubeVirt y red de Kubernetes.

## Antes de comenzar

- KubeVirt u OpenShift Virtualization está saludable.
- CDI está instalado y listo.
- El namespace permite crear VMs, DataVolumes, PVCs y Services.
- Existe StorageClass predeterminada o conoces su nombre.
- Elige una URL Fedora Cloud qcow2 confiable, accesible desde el clúster y compatible con cloud-init. Reemplaza `CHANGEME_IMAGE_URL` en el manifiesto.
- Reemplaza `CHANGEME_SSH_PUBLIC_KEY` por una clave pública si deseas SSH. El Service expone solo HTTP; la consola está disponible con `virtctl`.
- La plantilla apunta a imágenes Fedora cloud con cloud-init y paquete `httpd`; confirma datasource y gestor de paquetes de la imagen elegida.

## Despliegue

Revisa [el manifiesto](../manifests/capstone-functional-vm.yaml), reemplaza los marcadores y aplícalo:

```bash
kubectl apply -f workshop/manifests/capstone-functional-vm.yaml
kubectl -n kubevirt-workshop get datavolume,pvc,vm,vmi,svc
kubectl -n kubevirt-workshop wait --for=condition=Ready pvc/final-vm-disk --timeout=20m
kubectl -n kubevirt-workshop wait --for=condition=Ready vmi/final-functional-vm --timeout=10m
```

La importación puede tardar varios minutos. Revisa el progreso:

```bash
kubectl -n kubevirt-workshop describe datavolume final-vm-disk
kubectl -n kubevirt-workshop get pods
```

La VM debería iniciar automáticamente. Si no lo hace:

```bash
virtctl start final-functional-vm -n kubevirt-workshop
```

## Validar la inicialización y HTTP

Consulta consola y salida de cloud-init:

```bash
virtctl console final-functional-vm -n kubevirt-workshop
```

Sal de la consola con la secuencia indicada por virtctl (normalmente Ctrl+]).

En una terminal, reenvía el Service:

```bash
kubectl -n kubevirt-workshop port-forward service/final-vm-web 8080:80
```

En otra terminal:

```bash
curl --fail http://127.0.0.1:8080/
```

La respuesta esperada incluye: `KubeVirt capstone is working`. Esto confirma que la imagen se importó, la VM arrancó, cloud-init ejecutó, HTTP está activo, la red/Service llega al guest y port-forward funciona.

## Diagnóstico

```bash
kubectl -n kubevirt-workshop get vm,vmi,datavolume,pvc,pods,svc -o wide
kubectl -n kubevirt-workshop describe vmi final-functional-vm
kubectl -n kubevirt-workshop describe datavolume final-vm-disk
kubectl -n kubevirt-workshop get events --sort-by=.lastTimestamp
virtctl console final-functional-vm -n kubevirt-workshop
```

Causas frecuentes:
- **PVC/DataVolume Pending:** falta StorageClass, capacidad o CDI no llega a la URL.
- **La VM no se programa:** el nodo no expone virtualización, se agotó la cuota o hay selectores/taints incompatibles.
- **VM Running pero HTTP no responde:** cloud-init no terminó, la imagen carece de cloud-init/`httpd`, o el selector del Service no coincide.
- **Falla port-forward:** Service sin endpoints; inspecciona `kubectl get endpoints final-vm-web -n kubevirt-workshop` y etiquetas de VMI.
- **Falla de arranque:** URL no es qcow2 compatible o arquitectura guest incompatible con los nodos.

## Retos opcionales

1. Agrega un segundo disco con otro DataVolume y móntalo en el guest.
2. Cambia la página con cloud-init y despliega con otro nombre de VM.
3. Expón el Service con Ingress o Route si el entorno lo permite.
4. Define requests/límites de CPU y memoria y compara valores con el guest.
5. Documenta cómo cambiar la plantilla con GitOps.

## Limpieza

Detén y elimina los recursos de VM. La retención del PVC depende de la política de DataVolume/storage; inspecciónala antes de borrar.

```bash
kubectl delete -f workshop/manifests/capstone-functional-vm.yaml
kubectl get pvc -n kubevirt-workshop
```

Elimina el namespace solo después de confirmar que no deben conservarse datos.
