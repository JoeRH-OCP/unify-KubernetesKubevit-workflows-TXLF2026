# Laboratorio 3: Despliegue de KubeVirt y ciclo de vida de VMs

**Tiempo sugerido:** 3.5–4 horas para los módulos 5 y 6  
**Objetivo:** comprender el plano de control de KubeVirt, confirmar la instalación y crear/administrar una VM.

## Módulo 5: Conceptos de KubeVirt

KubeVirt extiende la API de Kubernetes con recursos de VM y ejecuta las cargas de VM en Pods administrados por KubeVirt.

- **virt-api:** endpoint de extensión para recursos de KubeVirt.
- **virt-controller:** observa VM/VMI y coordina su ciclo de vida.
- **virt-handler:** administra las VMIs asignadas a cada nodo.
- **libvirt/QEMU:** ejecuta VMs y administra dispositivos en el nodo.
- **CDI:** importa discos a PVCs y DataVolumes.

Objetos principales: **VirtualMachine (VM)** expresa configuración y ciclo de vida deseado; **VirtualMachineInstance (VMI)** es la instancia en ejecución; **DataVolume (DV)** importa o clona contenido de disco; **PVC** es el claim de disco persistente.

Una VM puede usar la red Pod con masquerade, un Service para acceso estable y discos respaldados por PVC. Multus agrega interfaces secundarias si el clúster está preparado.

## Módulo 6: Instalación y readiness

### Dos formas de tener KubeVirt en OpenShift

- **OpenShift Virtualization:** el producto con soporte, instalado desde OperatorHub con la documentación de Red Hat correspondiente a la versión. Administra KubeVirt y CDI mediante el recurso HyperConverged.
- **KubeVirt upstream:** las versiones del proyecto instaladas directamente. Es lo que usan los clústeres de demo de TXLF 2026. La automatización de `ansible/` lo instala con `virt_mode: kubevirt` (y antes elimina OpenShift Virtualization), o conserva OpenShift Virtualization con `virt_mode: cnv`. Nunca mezcles ambos en el mismo clúster.

Validaciones del instructor para OpenShift Virtualization:

```bash
oc get csv -n openshift-cnv
oc get hco -n openshift-cnv
oc get pods -n openshift-cnv
oc get crd | grep kubevirt
```

### Ruta para Kubernetes upstream

Estas son las versiones probadas para el workshop (Kubernetes 1.34 / OpenShift 4.21). Para OpenShift 4.18 (Kubernetes 1.31) usa KubeVirt v1.6.6 y CDI v1.63.1.

```bash
export KUBEVIRT_RELEASE=v1.9.1
kubectl apply -f "https://github.com/kubevirt/kubevirt/releases/download/${KUBEVIRT_RELEASE}/kubevirt-operator.yaml"
kubectl apply -f "https://github.com/kubevirt/kubevirt/releases/download/${KUBEVIRT_RELEASE}/kubevirt-cr.yaml"
kubectl -n kubevirt wait kv/kubevirt --for=condition=Available --timeout=10m

export CDI_RELEASE=v1.66.1
kubectl apply -f "https://github.com/kubevirt/containerized-data-importer/releases/download/${CDI_RELEASE}/cdi-operator.yaml"
kubectl apply -f "https://github.com/kubevirt/containerized-data-importer/releases/download/${CDI_RELEASE}/cdi-cr.yaml"
kubectl wait cdi/cdi --for=condition=Available --timeout=10m
```

En OpenShift, `ansible/site.yml` hace todo esto más los detalles propios de OpenShift (labels de Pod Security, StorageProfile para Ceph RBD Block/RWX, Ingress). La instalación y los permisos de workloads privilegiados son tarea del administrador del clúster.

**Checkpoint de readiness:** KubeVirt está Available; CDI saludable; nodos programables; StorageClass puede crear PVC; y el instructor probó una VM real.

## Crear e inspeccionar una VM

Para una prueba rápida, aplica la VM lista para usar del repositorio (usa un containerDisk de Fedora y tu clave SSH, consulta `ansible/manifests/README.md`):

```bash
kubectl apply -f https://raw.githubusercontent.com/JoeRH-OCP/unify-KubernetesKubevit-workflows-TXLF2026/main/ansible/manifests/01-vm-live.yaml
kubectl get vm,vmi -n demo-vms vm-live
```

Para el ejercicio persistente que sirve una aplicación, continúa con el [laboratorio final](04-capstone-functional-vm.es.md).

Comandos útiles:

```bash
kubectl get vm,vmi -A
kubectl describe vm CHANGEME
virtctl start CHANGEME
virtctl console CHANGEME
virtctl stop CHANGEME
```

Quienes usan OpenShift pueden usar `oc`. Instala `virtctl` compatible con la versión de la plataforma.

### Discusión guiada

1. Compara la VM con un Deployment: ¿qué representa el estado deseado y cuál la instancia activa?
2. Localiza el Pod virt-handler de un nodo e inspecciona logs (demostración del instructor).
3. Identifica dónde se almacena la imagen y cómo enlaza un PVC con una StorageClass.
4. Compara `containerDisk` (práctico, normalmente efímero) con un disco persistente basado en DataVolume.
5. Repasa requisitos de live migration: nodos compatibles, red/política, compatibilidad de CPU y almacenamiento compartido.

## Live migration opcional

Inténtala solo si el clúster y el almacenamiento de la VM están configurados explícitamente para ello (discos RWX, dos o más nodos programables, un modelo de CPU común). Los clústeres de demo de TXLF lo están: consulta el [Módulo 6 de la sesión de 90 minutos](../session/06-day2-operations.es.md) para ver el flujo completo. De lo contrario, explica el flujo y revisa readiness con la condición `LiveMigratable`; una migración fallida en un clúster no preparado no implica un fallo de KubeVirt.
