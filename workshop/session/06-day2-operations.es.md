# Módulo 6: Operaciones de día 2

**Tiempo:** 20 minutos
**Objetivo:** Haz lo que haces cada semana con VMs: parchar un nodo sin downtime, respaldar y restaurar, ver métricas y diagnosticar problemas. Todo con herramientas de Kubernetes.

Mantén abierta la página de `vm-web` del Módulo 1 donde puedas verla.

## Migración en vivo: mueve una VM en ejecución

`vm-web` ejecuta nginx dentro de una VM Fedora. La página le pregunta al cluster cada 2 segundos qué nodo ejecuta la VM.

```bash
kubectl get vmi -n demo-vms vm-web -o wide
```

Anota el `NODENAME`. Ahora mueve la VM en ejecución:

```bash
virtctl migrate vm-web -n demo-vms
kubectl get vmim -n demo-vms -w
```

Observa el navegador: la página muestra "Live migration in progress" y luego el nombre del nodo nuevo parpadea en naranja. La página nunca se recarga y nginx sigue respondiendo. Presiona Ctrl+C cuando la migración muestre `Succeeded`.

Desde la interfaz, el botón **»** (**Live Migrate**) en la página de `vm-web` en kubevirt-manager hace lo mismo.

Qué pasó:

1. KubeVirt inició un segundo Pod `virt-launcher` en otro nodo.
2. QEMU le copió la memoria del guest mientras la VM seguía en ejecución y luego hizo el cambio en milisegundos.
3. El disco no se movió: es un volumen Block/RWX, así que ambos nodos podían abrirlo.
4. El Service siguió al Pod nuevo, así que la URL siguió funcionando.

## Mantenimiento de nodos

Cuando un nodo necesita parches, no mueves VMs a mano. El spec de la VM dice qué hacer cuando se hace drain de su nodo:

```bash
kubectl get vm vm-web -n demo-vms -o jsonpath='{.spec.template.spec.evictionStrategy}{"\n"}'
```

`LiveMigrate` significa "si se hace drain de mi nodo, migrame, no me mates". Pruébalo de forma segura con un cordon:

```bash
NODE=$(kubectl get vmi -n demo-vms vm-web -o jsonpath='{.status.nodeName}')
kubectl cordon $NODE
virtctl migrate vm-web -n demo-vms
kubectl get vmi -n demo-vms vm-web -o wide -w
```

Presiona Ctrl+C cuando cambie el nodo y luego siempre deshaz el cordon:

```bash
kubectl uncordon $NODE
```

Con `kubectl drain`, cada VM con `evictionStrategy: LiveMigrate` migra de la misma forma, y los contenedores del nodo se reprograman como siempre. Un solo procedimiento de mantenimiento para ambos.

## Respaldo y restauración con snapshots

Usa `vm-clone-live`, la VM que creaste en el Módulo 4 con tu clave SSH. Guarda algunos "datos importantes" en ella:

```bash
virtctl ssh fedora@vm/vm-clone-live -n demo-vms -c 'echo "TXLF 2026 important data" | sudo tee /srv/data.txt'
```

Toma un snapshot de la VM en ejecución:

```bash
kubectl apply -f - <<'EOF'
apiVersion: snapshot.kubevirt.io/v1beta1
kind: VirtualMachineSnapshot
metadata:
  name: before-oops
  namespace: demo-vms
spec:
  source:
    apiGroup: kubevirt.io
    kind: VirtualMachine
    name: vm-clone-live
EOF
kubectl get vmsnapshot -n demo-vms before-oops -w
```

Presiona Ctrl+C cuando `READYTOUSE` sea `true`. El QEMU guest agent congeló los filesystems del guest para que el snapshot sea consistente, y Ceph tomó un snapshot CSI del disco.

Ahora, el error:

```bash
virtctl ssh fedora@vm/vm-clone-live -n demo-vms -c 'sudo rm -f /srv/data.txt; ls -l /srv'
```

Restaura. Una VM debe estar detenida para restaurar sus discos:

```bash
virtctl stop vm-clone-live -n demo-vms
kubectl wait vmi/vm-clone-live -n demo-vms --for=delete --timeout=120s
kubectl apply -f - <<'EOF'
apiVersion: snapshot.kubevirt.io/v1beta1
kind: VirtualMachineRestore
metadata:
  name: undo-oops
  namespace: demo-vms
spec:
  target:
    apiGroup: kubevirt.io
    kind: VirtualMachine
    name: vm-clone-live
  virtualMachineSnapshotName: before-oops
EOF
kubectl get vmrestore -n demo-vms undo-oops -w
```

Presiona Ctrl+C cuando `COMPLETE` sea `true`, luego inicia la VM y revisa el archivo:

```bash
virtctl start vm-clone-live -n demo-vms
kubectl wait vmi/vm-clone-live -n demo-vms --for=condition=AgentConnected --timeout=180s
virtctl ssh fedora@vm/vm-clone-live -n demo-vms -c 'cat /srv/data.txt'
```

Los datos volvieron, exactamente como estaban cuando tomaste el snapshot.

## Métricas

KubeVirt publica métricas de Prometheus para cada VM, y el monitoreo de OpenShift las recolecta junto a las métricas de los contenedores.

En la consola de OpenShift:

1. En el menú de la izquierda, haz clic en **Observe** y luego en **Metrics**.
2. Pega una consulta en el cuadro de expresión y haz clic en **Run queries**:

```text
rate(kubevirt_vmi_vcpu_seconds_total{namespace="demo-vms"}[2m])
```

```text
kubevirt_vmi_memory_domain_bytes{namespace="demo-vms"}
```

![Observe, Metrics en la consola de OpenShift con una consulta de KubeVirt](../assets/screenshots/console-metrics.png)

En kubevirt-manager las mismas métricas se grafican por VM:

1. **Virtual Machines**, haz clic en **vm-web**.
2. Haz clic en la pestaña **Monitoring**: gráficas de CPU, memoria, red y almacenamiento de la última hora.

![La pestaña Monitoring de vm-web en kubevirt-manager](../assets/screenshots/kvm-monitoring.png)

## Día 2 con Ansible

Todo lo que hiciste en este módulo es una llamada a la API de Kubernetes, así que también lo puedes automatizar con Ansible. Este laboratorio se construyó así: la carpeta `ansible/` que clonaste instala KubeVirt y crea todas las VMs del demo.

La colección [`kubevirt.core`](https://galaxy.ansible.com/ui/repo/published/kubevirt/core/) te da:

| Plugin | Qué hace |
|---|---|
| `kubevirt.core.kubevirt_vm` | Crear, cambiar, encender, apagar o borrar una VM, de forma declarativa |
| `kubevirt.core.kubevirt_vm_info`, `kubevirt_vmi_info` | Leer VMs e instancias en ejecución (estado, nodo, IPs) |
| `kubevirt.core.kubevirt` (inventario) | Convierte las VMs en ejecución en hosts de Ansible, agrupados por namespace y label |

Junto con `kubernetes.core.k8s` (snapshots, Services, cualquier otro objeto) cubre las dos capas:

- **La plataforma**: VMs, discos, snapshots y migraciones, a través de la API de Kubernetes.
- **El guest**: el plugin de inventario lista las VMs como hosts, así que tus playbooks de siempre (parches, usuarios, configuración) corren dentro de ellas como en cualquier servidor Linux.

Un archivo de inventario que encuentra las VMs del workshop:

```yaml
# kubevirt.yml (el nombre del archivo debe terminar en kubevirt.yml)
plugin: kubevirt.core.kubevirt
namespaces:
  - demo-vms
```

Un playbook que usa las dos capas:

```yaml
- name: Report where each VM runs
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Read the running VMs
      kubevirt.core.kubevirt_vmi_info:
        namespace: demo-vms
      register: vmis

    - name: Show VM and node
      ansible.builtin.debug:
        msg: "{{ item.metadata.name }} runs on {{ item.status.nodeName }}"
      loop: "{{ vmis.resources }}"

- name: Patch the guests like any Linux server
  hosts: all  # todas las VMs que el inventario encontró en demo-vms
  become: true
  tasks:
    - name: Update all packages
      ansible.builtin.dnf:
        name: "*"
        state: latest
```

No necesitas ejecutarlo hoy: Ansible no está instalado en la terminal web. Para llegar a los guests por SSH, Ansible debe correr donde la red de Pods sea alcanzable (por ejemplo en un Pod o en Ansible Automation Platform) o usar un Service NodePort/LoadBalancer para SSH (la opción `use_service` del inventario). Mira `ansible/roles/demo_vms` en el repo para ver ejemplos reales.

## Diagnóstico de problemas

La evidencia está donde está para cualquier Pod:

```bash
kubectl get events -n demo-vms --sort-by=.lastTimestamp | tail
kubectl describe vmi -n demo-vms vm-web | sed -n '/Conditions/,/Events/p'
```

| Síntoma | Revisa | Causa habitual |
|---|---|---|
| VMI atorada en `Scheduling` | `kubectl describe vmi`, eventos | Ningún nodo con CPU/RAM libre o `/dev/kvm`, un node selector |
| Importación del DataVolume atorada | `kubectl get dv`, logs del Pod importer | URL de la imagen, proxy o TLS |
| VM en `Running` pero la app caída | Endpoints del Service, consola del guest | Servicio del guest, cloud-init sin terminar |
| La migración falla | Condición `LiveMigratable`, eventos de migración | Disco que no es RWX, modelo de CPU distinto entre nodos |

## Checkpoint

Moviste una VM en ejecución sin downtime, usaste reglas de mantenimiento de nodos, restauraste una VM desde un snapshot y encontraste sus métricas y eventos. Sigue: los trade-offs honestos.
