# Módulo 5: Expón y observa VMs como cualquier aplicación

**Tiempo:** 15 minutos
**Objetivo:** Ve que una VM se expone con un Service y un Ingress normales, y que se monitorea con el mismo stack de métricas que los contenedores.

## Redes: un Service frente a una VM

`vm-web` es accesible desde tu navegador a través de dos objetos estándar de Kubernetes. Revísalos:

```bash
kubectl get svc,ingress -n demo-vms vm-web
kubectl get svc -n demo-vms vm-web -o jsonpath='{.spec.selector}{"\n"}'
```

El Service selecciona Pods con la etiqueta `vm.kubevirt.io/name: vm-web`. Cada Pod `virt-launcher` de esa VM tiene la etiqueta, por eso la URL siguió funcionando después de la migración. La VM usa la red de Pods con `masquerade`: desde fuera tiene la IP del Pod, igual que un contenedor.

Expón tu propia `vm-live` de la misma forma, esta vez con SSH:

```bash
virtctl expose vm vm-live -n demo-vms --name vm-live-ssh --port 22 --type ClusterIP
kubectl get svc,endpoints -n demo-vms vm-live-ssh
```

Desde cualquier Pod del cluster, `vm-live-ssh.demo-vms.svc:22` ahora llega a la VM. El mismo DNS, los mismos Services, la misma NetworkPolicy que cualquier aplicación.

## Observa: métricas que ya sabes usar

KubeVirt publica métricas de Prometheus para cada VM, y el monitoreo de OpenShift las recolecta. En la consola, abre **Observe, Metrics** y ejecuta:

```text
rate(kubevirt_vmi_vcpu_seconds_total{namespace="demo-vms"}[2m])
```

```text
kubevirt_vmi_memory_domain_bytes{namespace="demo-vms"}
```

```text
rate(kubevirt_vmi_network_receive_bytes_total{namespace="demo-vms",name="vm-web"}[2m])
```

kubevirt-manager grafica las mismas métricas por VM. Abre `vm-web` ahí y revisa las gráficas, la pestaña **Networking** (NIC, IP) y **Overview** (sistema operativo del guest, reportado por el guest agent).

## Troubleshooting: eventos y condiciones

Cuando algo falla, la evidencia está donde está para cualquier Pod:

```bash
kubectl get events -n demo-vms --sort-by=.lastTimestamp | tail
kubectl describe vmi -n demo-vms vm-web | sed -n '/Conditions/,/Events/p'
```

Condiciones útiles: `Ready`, `AgentConnected` (guest agent) y `LiveMigratable`. Si una VM no puede migrar, `LiveMigratable` dice por qué (por ejemplo, un disco que no es RWX).

| Síntoma | Dónde revisar | Causa común |
|---|---|---|
| VMI atorada en `Scheduling` | `kubectl describe vmi`, eventos | Ningún nodo con CPU/RAM libre o `/dev/kvm`, un node selector |
| Importación del DataVolume atorada | `kubectl get dv`, logs del Pod importer | URL de la imagen, proxy o TLS |
| VM en `Running` pero la aplicación caída | Endpoints del Service, consola del guest | Servicio del guest, cloud-init sin terminar |
| La migración falla | `LiveMigratable`, eventos de migración | Disco que no es RWX, modelo de CPU distinto entre nodos |

## Checkpoint

Una VM usa Services, Ingress, DNS, Prometheus y eventos como cualquier Pod. Siguiente: resumen y hacia dónde seguir.
