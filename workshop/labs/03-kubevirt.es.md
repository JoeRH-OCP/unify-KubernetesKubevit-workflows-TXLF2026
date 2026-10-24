# Laboratorio 3: Instala KubeVirt y verifica que esté listo

**Tiempo sugerido:** 60–90 minutos  
**Objetivo:** instalar KubeVirt y CDI en un cluster y confirmar que está listo para VMs. Cómo funciona KubeVirt y el ciclo de vida de las VMs están en los [Módulos 2 y 3 del taller](../session/02-how-kubevirt-works.es.md).

## Instalación y readiness

### Dos formas de tener KubeVirt en OpenShift

- **OpenShift Virtualization:** el producto con soporte, instalado desde OperatorHub con la documentación de Red Hat correspondiente a la versión ([Laboratorio 6](06-openshift-virtualization.es.md) lo explica paso a paso). Administra KubeVirt y CDI mediante el recurso HyperConverged.
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

## Siguiente paso

- Primera VM en el cluster nuevo: [Módulo 2 de la sesión](../session/02-how-kubevirt-works.es.md) (`manifests/01-vm-live.yaml`).
- Una VM persistente que sirve una aplicación: [Laboratorio 4 final](04-capstone-functional-vm.es.md).
- Live migration y mantenimiento de nodos: [Módulo 6 de la sesión](../session/06-day2-operations.es.md).
