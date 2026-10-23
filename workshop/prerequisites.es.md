# Prerrequisitos del entorno de laboratorio

## Entorno recomendado

Usa un clúster OpenShift preparado con OpenShift Virtualization compatible y saludable. También sirve Kubernetes upstream con versiones compatibles de KubeVirt y CDI. No mezcles las instrucciones de instalación upstream con el operador de OpenShift Virtualization.

## Lista de preparación del clúster

### Acceso y herramientas

- Una cuenta por participante con permisos para crear y consultar Pods, Deployments, Services, ConfigMaps, Secrets, PVCs, VMs y VMIs en el namespace del laboratorio.
- Acceso de administrador del clúster reservado al instructor para instalar componentes y resolver problemas globales.
- `kubectl` u `oc`; `virtctl` compatible con la versión instalada.
- Podman o Docker, terminal, editor YAML, curl y herramientas básicas de shell.
- DNS funcional, acceso al registry y conectividad hacia la imagen de VM seleccionada.

### Cómputo y virtualización

- Nodos worker con virtualización por hardware (Intel VT-x o AMD-V) expuesta al sistema operativo.
- Virtualización habilitada en BIOS/firmware del host físico o virtual.
- Capacidad suficiente para el clúster y las VMs concurrentes. Para el ejercicio final, reserva como mínimo 1 vCPU y 2 GiB de RAM por VM, más el overhead.
- En entornos anidados o cloud, confirma que el proveedor expone la virtualización. La emulación puede ser lenta y debe verificarse con la documentación de la versión usada.

### Almacenamiento

- StorageClass predeterminada funcional o nombre de una clase explícita.
- Aprovisionamiento dinámico de PVC con al menos 20 GiB por disco de arranque.
- CDI instalado y saludable para importar la imagen qcow2.
- Capacidad libre suficiente y política de reclaim conocida por el instructor.
- Live migration requiere almacenamiento compartido y modos de acceso/configuración compatibles; de lo contrario, trátala como explicación o demostración.

### Red

- Red de Pods y DNS operativos entre workloads.
- Services disponibles.
- Ingress/Route solo si el entorno los expone.
- NetworkPolicy solo si el CNI las aplica.
- Para el ejercicio final, configura la VM en la red Pod predeterminada con masquerade; Service más port-forward permite una comprobación HTTP repetible.
- Multus es opcional y requiere una NetworkAttachmentDefinition y red de nodos preparadas.

## Validación por plataforma

**OpenShift:** instala OpenShift Virtualization desde OperatorHub siguiendo la documentación de la versión. El recurso HyperConverged debe estar listo y los Pods saludables. Los participantes crean VMs con permisos de namespace; el operador administra SCC y configuración global.

**Kubernetes upstream:** instala versiones compatibles de KubeVirt y CDI. KubeVirt debe estar Available, los componentes CDI listos y las políticas de seguridad permitir los workloads de virtualización.

## Preflight del instructor

```bash
kubectl get nodes -o wide
kubectl get storageclass
kubectl get pods -A | grep -E 'kubevirt|virt-|cdi|data-importer'
kubectl get crd | grep -E 'kubevirt|cdi'
```

En OpenShift:

```bash
oc get hco -A
oc get pods -n openshift-cnv
oc get storageclass
oc get nodes -o wide
```

Confirma una URL qcow2 compatible con cloud-init y prueba la importación y una VM completa al menos un día antes del workshop.

## Namespace y cuotas

Crea un namespace por participante o equipo pequeño. Como punto de partida, asigna 2 vCPU, 4 GiB de RAM y 20–30 GiB de almacenamiento por participante, sujeto a capacidad y políticas. No otorgues permisos globales a los asistentes.

## Limitaciones conocidas

- Los clústeres locales a menudo carecen de virtualización anidada o RAM suficiente.
- Algunos servicios Kubernetes administrados no exponen virtualización por hardware.
- NetworkPolicy depende del CNI.
- El almacenamiento y la migración dependen del backend y sus modos de acceso.
- Que la API acepte el despliegue no garantiza que la VM pueda programarse; valida un guest real antes de la clase.
