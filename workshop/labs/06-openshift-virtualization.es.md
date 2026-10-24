# Laboratorio 6: OpenShift Virtualization (el producto)

**Tiempo sugerido:** 60–90 minutos  
**Objetivo:** instalar OpenShift Virtualization desde el catálogo de operadores, crear una VM desde el catálogo de la consola y con YAML, y ver qué agrega el producto sobre KubeVirt upstream.

OpenShift Virtualization (también llamado CNV) es la versión de KubeVirt y CDI con soporte de Red Hat. Es la misma API que usaste en la sesión (`VirtualMachine`, `DataVolume`, `virtctl`), instalada y actualizada por un solo operador, con interfaz en la consola, imágenes de arranque, plantillas y soporte de Red Hat.

> ⚠️ **Usa un cluster sin KubeVirt upstream.** Los clusters del workshop usan KubeVirt upstream. Nunca instales ambos en el mismo cluster. Usa otro cluster de OpenShift, o primero quita la instalación upstream con `ansible-navigator run teardown.yml -e confirm_teardown=true` desde la carpeta `ansible/`. Los nodos deben soportar virtualización (bare metal, o instancias en la nube con virtualización anidada).

## KubeVirt upstream u OpenShift Virtualization

| | KubeVirt upstream | OpenShift Virtualization |
|---|---|---|
| Instalación y actualización | YAML de release para KubeVirt y CDI, uno por uno | Un operador (HyperConverged) que instala KubeVirt, CDI, complementos de red y plantillas, y se actualiza con OpenShift |
| Interfaz | Herramientas de terceros, como kubevirt-manager en este workshop | Sección **Virtualization** en la consola de OpenShift |
| Imágenes de arranque | Las importas tú (`golden-image` en el Módulo 4) | Imágenes de RHEL, CentOS Stream y Fedora que se actualizan solas |
| Tamaños de VM | Escribes CPU y memoria en cada VM | Instance types (`u1.small`, `u1.medium`...) y preferencias por sistema operativo |
| Monitoreo | Métricas de Prometheus | Las mismas métricas más dashboards y alertas |
| Soporte | Comunidad | Red Hat, con una versión probada para cada release de OpenShift |

## Instala el operador

### Desde la consola

1. Entra a la consola de OpenShift como cluster admin.
2. Abre **Operators**, **OperatorHub** (en consolas más nuevas: **Ecosystem**, **Software Catalog**) y busca **OpenShift Virtualization**.
3. Haz clic en **Install**, deja los valores por defecto (canal `stable`, namespace `openshift-cnv`) y haz clic en **Install** otra vez.
4. Cuando el operador muestre **Succeeded**, haz clic en **Create HyperConverged**, deja los valores por defecto y haz clic en **Create**.
5. Espera a que la consola muestre la sección **Virtualization** en el menú de la izquierda (de 5 a 10 minutos).

### Con YAML

Los mismos pasos como objetos de Kubernetes. OLM (el Operator Lifecycle Manager) lee la Subscription e instala el operador:

```bash
oc apply -f - <<'EOF'
apiVersion: v1
kind: Namespace
metadata:
  name: openshift-cnv
---
apiVersion: operators.coreos.com/v1
kind: OperatorGroup
metadata:
  name: kubevirt-hyperconverged-group
  namespace: openshift-cnv
spec:
  targetNamespaces:
    - openshift-cnv
---
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: hco-operatorhub
  namespace: openshift-cnv
spec:
  source: redhat-operators
  sourceNamespace: openshift-marketplace
  name: kubevirt-hyperconverged
  channel: stable
EOF
oc get csv -n openshift-cnv -w
```

Presiona Ctrl+C cuando la fase del CSV sea `Succeeded`. Luego crea el recurso HyperConverged, el único objeto que configura todo el stack:

```bash
oc apply -f - <<'EOF'
apiVersion: hco.kubevirt.io/v1beta1
kind: HyperConverged
metadata:
  name: kubevirt-hyperconverged
  namespace: openshift-cnv
spec: {}
EOF
oc wait hco kubevirt-hyperconverged -n openshift-cnv --for=condition=Available --timeout=15m
```

Mira lo que creó:

```bash
oc get kubevirt,cdi,ssp,networkaddonsconfig -A
oc get pods -n openshift-cnv
```

Los recursos `KubeVirt` y `CDI` son los mismos que crearías a mano con upstream. El operador es su dueño: cambia la configuración en el recurso HyperConverged, no en ellos.

## Imágenes de arranque e instance types

El producto mantiene un conjunto de imágenes de arranque listas en su propio namespace:

```bash
oc get datasources -n openshift-virtualization-os-images
oc get dataimportcrons -n openshift-virtualization-os-images
```

Un `DataImportCron` revisa periódicamente si hay una imagen nueva y la importa; el `DataSource` siempre apunta a la más reciente. Esto reemplaza la importación manual de `golden-image` del Módulo 4.

Los tamaños de VM vienen como instance types, como los flavors de la nube, y las preferencias ponen los dispositivos correctos para cada sistema operativo:

```bash
oc get virtualmachineclusterinstancetypes
oc get virtualmachineclusterpreferences
```

## Crea una VM desde el catálogo

1. En la consola, abre **Virtualization**, **Catalog**.
2. En la pestaña **InstanceTypes**, en **Select volume to boot from**, haz clic en **fedora**.
3. En **Select InstanceType**, elige **U series**, tamaño **small** (`u1.small`).
4. En **VirtualMachine details**, elige el proyecto `demo-vms`, escribe el nombre `vm-catalog` y agrega tu llave SSH pública.
5. Haz clic en **Create VirtualMachine**. Se abre la página de la VM y la VM arranca.
6. Prueba las pestañas: **Overview** (estado y métricas), **Console** (VNC y serial en el navegador), **Snapshots**, y el menú **Actions** (**Stop**, **Restart**, **Migrate**).

## La misma VM en YAML

El catálogo escribe un `VirtualMachine` normal. Esta es la misma VM a mano; fíjate que no tiene CPU, memoria ni bus de disco, porque el instance type y la preferencia los ponen:

```bash
oc apply -f - <<'EOF'
apiVersion: kubevirt.io/v1
kind: VirtualMachine
metadata:
  name: vm-catalog-yaml
  namespace: demo-vms
spec:
  runStrategy: Always
  instancetype:
    kind: VirtualMachineClusterInstancetype
    name: u1.small
  preference:
    kind: VirtualMachineClusterPreference
    name: fedora
  dataVolumeTemplates:
    - metadata:
        name: vm-catalog-yaml-rootdisk
      spec:
        sourceRef:
          kind: DataSource
          name: fedora
          namespace: openshift-virtualization-os-images
        storage:
          resources:
            requests:
              storage: 30Gi
  template:
    spec:
      domain:
        devices: {}
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
            name: vm-catalog-yaml-rootdisk
        - name: cloudinit
          cloudInitNoCloud:
            userData: |
              #cloud-config
              hostname: vm-catalog-yaml
EOF
oc get vm,dv -n demo-vms vm-catalog-yaml
```

Usa el Secret `demo-ssh-key` de la sesión (Módulo 1); créalo en tu namespace si no existe. Todo lo demás de la sesión funciona igual: `virtctl ssh`, `virtctl migrate`, snapshots, Services e Ingress.

## Operadores que completan la plataforma

| Operador | Qué agrega |
|---|---|
| Migration Toolkit for Virtualization (MTV) | Mueve VMs en lote desde VMware vSphere, Red Hat Virtualization, OpenStack o archivos OVA |
| Kubernetes NMState | Bridges, bonds y VLANs en los nodos, para VMs en redes existentes (Multus) |
| OpenShift Data Foundation | Almacenamiento Ceph con volúmenes Block/RWX y snapshots, necesarios para live migration y clones rápidos |
| Node Health Check, Self Node Remediation, Fence Agents Remediation | Reinician en otro nodo las VMs de un nodo que falló |
| Kube Descheduler | Rebalancea las VMs en ejecución entre nodos con live migration |

## OpenShift Virtualization con este repo

La automatización en `ansible/` soporta ambas capas. Con `virt_mode: cnv` conserva OpenShift Virtualization y solo agrega lo que necesita el workshop (kubevirt-manager, branding, VMs del demo):

```bash
cd ~/txlf/ansible
ansible-navigator run site.yml -e virt_mode=cnv
```

Mira la sección "Virtualization mode" de `ansible/README.md` para ver las diferencias.

## Limpieza

```bash
oc delete vm -n demo-vms vm-catalog vm-catalog-yaml
```

Para desinstalar el producto: borra primero el recurso HyperConverged y espera a que desaparezca, luego la Subscription, el CSV y el namespace `openshift-cnv`. Si borras primero el namespace, el cluster se queda atorado.
