# Módulo 2: Una VM es un Pod (con QEMU adentro)

**Tiempo:** 15 minutos
**Objetivo:** Ve cómo KubeVirt agrega máquinas virtuales a la API de Kubernetes, crea una con `kubectl apply` y encuentra las piezas de Linux que ya conoces: un proceso, un disco, una interfaz de red.

## Kubernetes aprendió una palabra nueva

KubeVirt es un add-on. No reemplaza a Kubernetes; lo extiende con nuevos tipos de recursos:

```bash
kubectl get kubevirt -n kubevirt
kubectl api-resources --api-group=kubevirt.io
```

| Objeto | Piénsalo como |
|---|---|
| `VirtualMachine` (VM) | La definición: CPU, memoria, discos, NICs y si debe estar en ejecución. Como un Deployment. |
| `VirtualMachineInstance` (VMI) | La VM que está corriendo en este momento. Como un Pod. |
| Pod `virt-launcher` | El Pod que contiene el proceso QEMU de una VMI. |
| `DataVolume` | Una imagen de disco que CDI importa o clona en un PVC. |

Los componentes también corren como Pods normales:

```bash
kubectl get pods -n kubevirt
```

`virt-api` y `virt-controller` son el cerebro; `virt-handler` corre en cada nodo y ahí se comunica con libvirt y QEMU.

## Crea una VM con kubectl

Primero revisa el manifiesto: es YAML normal, como cualquier otra carga de trabajo.

```bash
cat manifests/01-vm-live.yaml
kubectl apply -f manifests/01-vm-live.yaml
kubectl get vm,vmi -n demo-vms vm-live -w
```

Presiona Ctrl+C cuando la VMI esté en `Running` (entre 30 y 60 segundos). El disco viene de una imagen de contenedor (`containerDisk`), así que no hubo nada que importar.

## Encuentra el Pod y el proceso

```bash
kubectl get pod -n demo-vms -l vm.kubevirt.io/name=vm-live -o wide
```

Ese Pod es la VM. Mira dentro de su contenedor `compute`, donde libvirt ejecuta QEMU:

```bash
POD=$(kubectl get pod -n demo-vms -l vm.kubevirt.io/name=vm-live -o name)
kubectl exec -n demo-vms $POD -c compute -- virsh list
```

Kubernetes lo programa, lo reinicia y le pone límites como a cualquier Pod. Los requests de CPU y memoria vienen del spec de la VM.

## Entra al guest

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

Dos formas más de entrar, sin SSH:

```bash
virtctl console vm-quick -n demo-vms
```

La consola serial muestra el banner de TXLF de `/etc/issue`. Sal con Ctrl+].

## Ciclo de vida: los mismos verbos, objetos nuevos

```bash
virtctl stop vm-live -n demo-vms
kubectl get vm,vmi,pod -n demo-vms | grep vm-live
virtctl start vm-live -n demo-vms
```

Al detenerla se eliminan la VMI y su Pod; el objeto VM se queda, como cuando escalas un Deployment a cero.

## Checkpoint

Creaste una VM con `kubectl apply`, encontraste su Pod y su proceso QEMU, y entraste al guest. Siguiente: dónde viven sus discos.
