# Laboratorio 3 — Despliegue de KubeVirt y ciclo de vida de VMs

**Tiempo sugerido:** 3.5–4 horas para los módulos 5 y 6  
**Objetivo:** comprender el plano de control de KubeVirt, confirmar la instalación y crear/administrar una VM.

## Módulo 5 — Conceptos de KubeVirt

KubeVirt extiende la API de Kubernetes con recursos de VM y ejecuta las cargas de VM en Pods administrados por KubeVirt.

- **virt-api:** endpoint de extensión para recursos de KubeVirt.
- **virt-controller:** observa VM/VMI y coordina su ciclo de vida.
- **virt-handler:** administra las VMIs asignadas a cada nodo.
- **libvirt/QEMU:** ejecuta VMs y administra dispositivos en el nodo.
- **CDI:** importa discos a PVCs y DataVolumes.

Objetos principales: **VirtualMachine (VM)** expresa configuración y ciclo de vida deseado; **VirtualMachineInstance (VMI)** es la instancia en ejecución; **DataVolume (DV)** importa o clona contenido de disco; **PVC** es el claim de disco persistente.

Una VM puede usar la red Pod con masquerade, un Service para acceso estable y discos respaldados por PVC. Multus agrega interfaces secundarias si el clúster está preparado.

## Módulo 6 — Instalación y readiness

### Ruta para OpenShift Virtualization

Instala OpenShift Virtualization desde OperatorHub con la documentación de la versión. El administrador selecciona namespace y suscripción compatibles, y crea o valida el recurso HyperConverged. No apliques manifiestos upstream de KubeVirt en esta plataforma.

```bash
oc get csv -n openshift-cnv
oc get hco -n openshift-cnv
oc get pods -n openshift-cnv
oc get crd | grep kubevirt
```

### Ruta para Kubernetes upstream

Usa las guías oficiales de KubeVirt y CDI. Estos comandos ilustran el flujo con manifiestos del operador; fija y revisa una versión antes del workshop:

```bash
export KUBEVIRT_RELEASE=CHANGEME
kubectl apply -f "https://github.com/kubevirt/kubevirt/releases/download/${KUBEVIRT_RELEASE}/kubevirt-operator.yaml"
kubectl apply -f "https://github.com/kubevirt/kubevirt/releases/download/${KUBEVIRT_RELEASE}/kubevirt-cr.yaml"
kubectl -n kubevirt wait kv/kubevirt --for=condition=Available --timeout=10m
```

Instala CDI siguiendo la guía oficial correspondiente a la versión y confirma que operador, controller, API server y upload proxy estén listos. La instalación y los permisos de workloads privilegiados son tarea del administrador.

**Checkpoint de readiness:** KubeVirt está Available; CDI saludable; nodos programables; StorageClass puede crear PVC; y el instructor probó una VM real.

## Crear e inspeccionar una VM

Para una prueba rápida, usa el ejemplo quickstart adecuado al entorno. Para el ejercicio persistente que sirve una aplicación, continúa con el [laboratorio final](04-capstone-functional-vm.es.md).

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

Inténtala solo si el clúster y el almacenamiento de la VM están configurados explícitamente para ello. De lo contrario, explica el flujo y revisa readiness; una migración fallida en un clúster no preparado no implica un fallo de KubeVirt.
