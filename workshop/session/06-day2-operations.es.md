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

KubeVirt publica métricas de Prometheus para cada VM, y el monitoreo de OpenShift las recolecta junto a las métricas de los contenedores. En la consola, abre **Observe, Metrics** y ejecuta:

```text
rate(kubevirt_vmi_vcpu_seconds_total{namespace="demo-vms"}[2m])
```

```text
kubevirt_vmi_memory_domain_bytes{namespace="demo-vms"}
```

kubevirt-manager dibuja las mismas métricas por VM: abre `vm-web` ahí y mira sus gráficas.

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
