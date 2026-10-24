# Módulo 3: Ciclo de vida de la VM

**Tiempo:** 10 minutos
**Objetivo:** Inicia sesión en una VM, usa su consola y detenla, iníciala y reiníciala con las mismas herramientas de Kubernetes.

## Inicia sesión en el guest

```bash
virtctl ssh fedora@vm/vm-live -n demo-vms
```

Dentro de la VM, todo es un sistema Fedora normal:

```bash
uname -r
ip -br addr
lsblk
exit
```

¿No tienes SSH? Cada VM también tiene una consola serial, incluso antes de que su red esté lista:

```bash
virtctl console vm-quick -n demo-vms
```

La consola muestra el banner de TXLF desde `/etc/issue`. Sal con Ctrl+]. También hay una consola gráfica (VNC); kubevirt-manager la muestra en el navegador en **Console**.

## Detener, iniciar, reiniciar

```bash
virtctl stop vm-live -n demo-vms
kubectl get vm,vmi,pod -n demo-vms | grep vm-live
```

Al detenerla se eliminan la VMI y su Pod; el objeto VM se queda, con su definición y sus discos. Es como escalar un Deployment a cero.

```bash
virtctl start vm-live -n demo-vms
kubectl get vmi -n demo-vms vm-live -w
```

Presiona Ctrl+C cuando esté en `Running`. Para reiniciarla:

```bash
virtctl restart vm-live -n demo-vms
```

## Quién decide si una VM corre: runStrategy

```bash
kubectl get vm -n demo-vms -o custom-columns=NAME:.metadata.name,STRATEGY:.spec.runStrategy,STATUS:.status.printableStatus
```

| runStrategy | Comportamiento |
|---|---|
| `Always` | La mantiene en ejecución; la reinicia si se detiene o si falla su nodo |
| `Halted` | La mantiene detenida |
| `Manual` | Tú la inicias y la detienes; nada la reinicia por ti |
| `RerunOnFailure` | La reinicia solo si falla |

`virtctl start` y `virtctl stop` solo cambian este campo. Así funciona Kubernetes: tú declaras el estado y un controller lo hace realidad.

## Lo mismo en la interfaz

Abre kubevirt-manager, **Virtual Machines**, y elige `vm-live`: los botones de arriba (pausar, iniciar, detener, reiniciar) llaman a la misma API. En las pestañas **Details**, **Networking** y **Disks** ves lo que declaró el YAML.

## Checkpoint

Iniciaste sesión con SSH y con la consola serial, y controlaste la VM con `virtctl` y `runStrategy`. Lo que sigue: dónde viven sus discos.
