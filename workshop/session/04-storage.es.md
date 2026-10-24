# Módulo 4: Almacenamiento (los discos son PVCs)

**Tiempo:** 15 minutos
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

Este es `manifests/02-vm-clone-live.yaml`. Es el mismo tipo de VM, pero su disco es un clon de `golden-image`:

```yaml
apiVersion: kubevirt.io/v1
kind: VirtualMachine
metadata:
  name: vm-clone-live
  namespace: demo-vms
  labels:
    app.kubernetes.io/part-of: txlf-2026
    app.kubernetes.io/component: clone
spec:
  runStrategy: Always
  dataVolumeTemplates:
    - metadata:
        name: vm-clone-live-rootdisk
        labels:
          app.kubernetes.io/part-of: txlf-2026
      spec:
        source:
          pvc:
            namespace: demo-vms
            name: golden-image
        storage:
          storageClassName: ocs-external-storagecluster-ceph-rbd
          volumeMode: Block
          accessModes:
            - ReadWriteMany
          resources:
            requests:
              storage: 10Gi
  template:
    metadata:
      labels:
        app.kubernetes.io/part-of: txlf-2026
        app.kubernetes.io/component: clone
    spec:
      domain:
        cpu:
          cores: 1
          sockets: 1
          threads: 1
        # kubevirt-manager reads cpu cores/sockets/threads and resources.requests.memory
        resources:
          requests:
            memory: 2Gi
        devices:
          disks:
            - name: rootdisk
              disk:
                bus: virtio
            - name: cloudinit
              disk:
                bus: virtio
          interfaces:
            - name: default
              masquerade: {}
      networks:
        - name: default
          pod: {}
      evictionStrategy: LiveMigrate
      accessCredentials:
        - sshPublicKey:
            source:
              secret:
                secretName: demo-ssh-key
            propagationMethod:
              noCloud: {}
      volumes:
        - name: rootdisk
          dataVolume:
            name: vm-clone-live-rootdisk
        - name: cloudinit
          cloudInitNoCloud:
            userData: |
              #cloud-config
              hostname: vm-clone-live
```

| Parte | Qué hace |
|---|---|
| `dataVolumeTemplates` | Crea el disco propio de la VM, `vm-clone-live-rootdisk`, clonando el PVC `golden-image` |
| `storage` | StorageClass explícita, modo `Block`, `ReadWriteMany`, 10Gi (al menos el tamaño del origen) |
| `volumes.dataVolume` | La VM arranca desde ese disco clonado |
| `evictionStrategy: LiveMigrate` | Si su nodo se drena, la VM migra en lugar de detenerse (Módulo 6) |
| `accessCredentials`, `cloudInitNoCloud` | Igual que en `vm-live`: tu llave SSH y un hostname |

Aplícalo y observa el clon:

```bash
cd ~/txlf/ansible
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

`vm-web`, de `vm-clone-1` a `vm-clone-3` y tu nueva `vm-clone-live` partieron de `golden-image`.

Míralo en kubevirt-manager:

1. Menú de la izquierda, **Virtual Machines**, y haz clic en **vm-clone-live**.
2. Haz clic en la pestaña **Disks**. El renglón `rootdisk` muestra el DataVolume, su tamaño, el modo de acceso, la StorageClass y el origen `pvc (demo-vms - golden-image)`.

![La pestaña Disks de vm-clone-live en kubevirt-manager](../assets/screenshots/kvm-disks.png)

## Checkpoint

Un disco de VM es un PVC. Importar una imagen y clonar una VM son operaciones de almacenamiento de Kubernetes que se hacen con CSI. Lo que sigue: cómo se comunican las VMs y los contenedores.
