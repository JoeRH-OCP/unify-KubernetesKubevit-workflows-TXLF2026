# Módulo 3: Los discos son PVCs (y los clones toman segundos)

**Tiempo:** 15 minutos
**Objetivo:** Ve cómo los discos de las VMs se mapean al almacenamiento de Kubernetes y crea una VM nueva a partir de una golden image con un clon a nivel de almacenamiento.

## La golden image

Cuando el instructor preparó tu cluster, CDI importó la imagen cloud de Fedora 44 desde `download.fedoraproject.org` a un PVC:

```bash
kubectl get dv,pvc -n demo-vms golden-image
kubectl get dv -n demo-vms golden-image -o jsonpath='{.spec.source.http.url}{"\n"}'
```

Esa importación es la forma más simple de migración de cargas de trabajo: una imagen de disco existente, de fuera del cluster, se convierte en un volumen de Kubernetes. El mismo mecanismo importa desde registries, S3 o una subida desde tu laptop.

Mira cómo se almacena el disco:

```bash
kubectl get pvc -n demo-vms golden-image -o custom-columns=NAME:.metadata.name,MODE:.spec.volumeMode,ACCESS:.spec.accessModes,CLASS:.spec.storageClassName
```

- **Block:** la VM recibe un dispositivo de bloque crudo, sin sistema de archivos de por medio.
- **ReadWriteMany (RWX):** dos nodos pueden abrir el disco al mismo tiempo. Eso es lo que hace posible la migración en vivo en el Módulo 4.
- **StorageClass:** Ceph RBD de OpenShift Data Foundation; funciona cualquier driver CSI con estas características.

## Cómo clona CDI

```bash
kubectl get storageprofile ocs-external-storagecluster-ceph-rbd -o jsonpath='{.status}{"\n"}'
```

`cloneStrategy: snapshot` significa que CDI clona tomando un snapshot CSI del origen y restaurándolo. No se copian datos por la red.

## Clona una VM nueva

```bash
cat manifests/02-vm-clone-live.yaml
kubectl apply -f manifests/02-vm-clone-live.yaml
kubectl get dv -n demo-vms vm-clone-live-rootdisk -w
```

Ctrl+C cuando el DataVolume muestre `Succeeded`. Un disco de 10 GiB debería estar listo en segundos. Luego:

```bash
kubectl get vmi -n demo-vms vm-clone-live
kubectl get volumesnapshot -n demo-vms
```

El VolumeSnapshot es lo que CDI usó para hacer el clon.

## Todos tus discos de VM

```bash
kubectl get pvc -n demo-vms
```

`vm-web`, de `vm-clone-1` a `vm-clone-3` y tu nueva `vm-clone-live` partieron de `golden-image`. En kubevirt-manager, abre **Virtual Machines**, elige `vm-clone-live` y revisa la pestaña **Disks**: el origen es `pvc (demo-vms - golden-image)`.

## Checkpoint

Un disco de VM es un PVC. Importar una imagen y clonar una VM son operaciones de almacenamiento de Kubernetes, hechas con snapshots CSI. Siguiente: mover una VM en ejecución sin detenerla.
