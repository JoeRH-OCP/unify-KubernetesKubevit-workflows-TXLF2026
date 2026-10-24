# Módulo 4: Almacenamiento (los discos son PVCs)

**Tiempo:** 12 minutos
**Objetivo:** Ver cómo los discos de una VM se mapean al almacenamiento de Kubernetes y crear una VM nueva a partir de una golden image con un clon a nivel de almacenamiento.

## La golden image

Cuando el instructor preparó tu cluster, CDI (el Containerized Data Importer) importó la imagen cloud de Fedora 44 desde `download.fedoraproject.org` a un PVC:

```bash
kubectl get dv,pvc -n demo-vms golden-image
kubectl get dv -n demo-vms golden-image -o jsonpath='{.spec.source.http.url}{"\n"}'
```

El mismo mecanismo importa desde registries de contenedores, S3 o una carga desde tu laptop. También es la forma en que llegan los discos de VMs existentes de otras plataformas.

Revisa cómo se almacena el disco:

```bash
kubectl get pvc -n demo-vms golden-image -o 'custom-columns=NAME:.metadata.name,MODE:.spec.volumeMode,ACCESS:.spec.accessModes,CLASS:.spec.storageClassName'
```

- **Block:** la VM recibe un dispositivo de bloque crudo, sin sistema de archivos de por medio.
- **ReadWriteMany (RWX):** dos nodos pueden abrir el disco al mismo tiempo. Eso es lo que hace posible la migración en vivo en el Módulo 6.
- **StorageClass:** aquí es Ceph RBD de OpenShift Data Foundation; funciona cualquier driver CSI con estas capacidades.

## Cómo clona CDI

```bash
kubectl get storageprofile ocs-external-storagecluster-ceph-rbd -o jsonpath='{.status}{"\n"}'
```

`cloneStrategy: snapshot` significa que CDI clona tomando un snapshot CSI del origen y restaurándolo. No se copian datos por la red.

## Clona una VM nueva

```bash
cd ~/txlf/ansible
cat manifests/02-vm-clone-live.yaml
kubectl apply -f manifests/02-vm-clone-live.yaml
kubectl get dv -n demo-vms vm-clone-live-rootdisk -w
```

Presiona Ctrl+C cuando el DataVolume muestre `Succeeded`. Un disco de 10 GiB debería estar listo en segundos. Después:

```bash
kubectl get vmi -n demo-vms vm-clone-live
kubectl get volumesnapshot -n demo-vms
```

El VolumeSnapshot es lo que CDI usó para hacer el clon.

## Todos los discos de VM que tienes

```bash
kubectl get pvc -n demo-vms
```

`vm-web`, de `vm-clone-1` a `vm-clone-3` y tu nueva `vm-clone-live` partieron de `golden-image`. En kubevirt-manager, abre `vm-clone-live` y revisa la pestaña **Disks**: el origen es `pvc (demo-vms - golden-image)`.

## Checkpoint

Un disco de VM es un PVC. Importar una imagen y clonar una VM son operaciones de almacenamiento de Kubernetes que se hacen con CSI. Lo que sigue: cómo se comunican las VMs y los contenedores.
