# Módulo 2: Cómo funciona KubeVirt (una VM es un Pod)

**Tiempo:** 15 minutos
**Objetivo:** Quitarle el misterio: ver qué le agrega KubeVirt a Kubernetes, crear una VM con `kubectl apply` y encontrar detrás de ella las piezas de Linux que ya conoces.

## Qué es KubeVirt (y qué no es)

KubeVirt es un complemento open source para Kubernetes y un proyecto de la CNCF. No reemplaza lo que ya sabes de hipervisores: por debajo usa los mismos KVM, QEMU y libvirt que encuentras en cualquier host de virtualización Linux. Lo que cambia es quién los controla: la API de Kubernetes.

Preocupaciones comunes, y las respuestas cortas:

| Preocupación | Realidad |
|---|---|
| "Mis VMs se convierten en contenedores" | No. El guest es una VM completa con su propio kernel, que arranca una imagen de sistema operativo normal. |
| "Es lento o emulado" | No. Usa virtualización por hardware con KVM, como cualquier hipervisor Linux. |
| "Tengo que reescribir mis aplicaciones" | No. La VM ejecuta el mismo sistema operativo y la misma aplicación; solo cambia la forma de administrarla. |
| "Pierdo funciones de mis VMs" | Migración en vivo, snapshots, clones, consolas, cloud-init y múltiples NICs: todo está ahí. |

## Kubernetes aprendió una palabra nueva

KubeVirt extiende la API con nuevos tipos de recursos:

```bash
kubectl get kubevirt -A
kubectl api-resources --api-group=kubevirt.io
```

| Objeto | Piénsalo como |
|---|---|
| `VirtualMachine` (VM) | La definición: CPU, memoria, discos, NICs y si debe estar en ejecución. Como un Deployment. |
| `VirtualMachineInstance` (VMI) | La VM que está corriendo en este momento. Como un Pod. |
| Pod `virt-launcher` | El Pod que contiene el proceso de QEMU de una VMI. |
| `DataVolume` | Una imagen de disco que CDI importa o clona en un PVC. |

Los componentes de KubeVirt también corren como Pods normales:

```bash
kubectl get pods -n kubevirt
```

`virt-api` y `virt-controller` son el plano de control; `virt-handler` corre en cada nodo y se comunica ahí con libvirt y QEMU.

## Crea una VM con kubectl

El manifest es YAML normal, como cualquier otra carga de trabajo. Este es `manifests/01-vm-live.yaml`:

```yaml
apiVersion: kubevirt.io/v1
kind: VirtualMachine
metadata:
  name: vm-live
  namespace: demo-vms
  labels:
    app.kubernetes.io/part-of: txlf-2026
    app.kubernetes.io/component: vm-live
spec:
  runStrategy: Always
  template:
    metadata:
      labels:
        app.kubernetes.io/part-of: txlf-2026
        app.kubernetes.io/component: vm-live
    spec:
      domain:
        cpu:
          cores: 1
          sockets: 1
          threads: 1
        # kubevirt-manager reads cpu cores/sockets/threads and resources.requests.memory
        resources:
          requests:
            memory: 2Gi
        devices:
          disks:
            - name: containerdisk
              disk:
                bus: virtio
            - name: cloudinit
              disk:
                bus: virtio
          interfaces:
            - name: default
              masquerade: {}
      networks:
        - name: default
          pod: {}
      accessCredentials:
        - sshPublicKey:
            source:
              secret:
                secretName: demo-ssh-key
            propagationMethod:
              noCloud: {}
      volumes:
        - name: containerdisk
          containerDisk:
            image: quay.io/containerdisks/fedora:44-1.7
        - name: cloudinit
          cloudInitNoCloud:
            userData: |
              #cloud-config
              hostname: vm-live
              write_files:
                - path: /etc/motd
                  content: |
                    Texas Linux Fest 2026 - created live with kubectl apply
```

| Parte | Qué hace |
|---|---|
| `kind: VirtualMachine`, `runStrategy: Always` | Una definición de VM que debe estar siempre en ejecución |
| `domain.cpu`, `resources.requests.memory` | 1 vCPU y 2 GiB de RAM; Kubernetes usa la memoria como request del Pod al programar la VM |
| `devices.disks` y `volumes` | Dos discos: el del sistema operativo desde una imagen de contenedor (`containerDisk`) y un disco pequeño de cloud-init |
| `interfaces` y `networks` | Una NIC en la red de Pods con `masquerade`: la VM usa la IP del Pod |
| `accessCredentials` | KubeVirt copia tu llave pública del Secret `demo-ssh-key` al guest mediante cloud-init |
| `cloudInitNoCloud.userData` | Configuración del primer arranque: hostname y un mensaje de bienvenida |

Aplícalo y observa cómo arranca:

```bash
cd ~/txlf/ansible
kubectl apply -f manifests/01-vm-live.yaml
kubectl get vm,vmi -n demo-vms vm-live -w
```

Presiona Ctrl+C cuando la VMI esté en `Running` (entre 30 y 60 segundos). Su disco viene de una imagen de contenedor (`containerDisk`), así que no hubo nada que importar.

## Encuentra el Pod y el proceso de QEMU

```bash
kubectl get pod -n demo-vms -l vm.kubevirt.io/name=vm-live -o wide
```

Ese Pod es la VM. Revisa dentro de su contenedor `compute`, donde libvirt ejecuta QEMU:

```bash
POD=$(kubectl get pod -n demo-vms -l vm.kubevirt.io/name=vm-live -o name)
kubectl exec -n demo-vms $POD -c compute -- virsh list
```

Kubernetes programa, reinicia y limita este Pod como cualquier otro. El scheduler, las cuotas, RBAC y los logs de auditoría que ya usas con contenedores ahora también aplican a las VMs: un solo plano de control.

## Casos de uso

| Caso de uso | Por qué ayuda KubeVirt |
|---|---|
| Aplicaciones legacy o de proveedores que no se pueden contenerizar | Ejecútalas en la misma plataforma que las aplicaciones nuevas |
| Modernización gradual | Conserva la VM y mueve piezas a contenedores una a la vez |
| Consolidación de plataformas | Un equipo, una API y un solo conjunto de herramientas en lugar de dos stacks |
| Entornos de desarrollo y CI | VMs bajo demanda a partir de YAML y Git |
| Workloads que necesitan su propio kernel | Módulos del kernel, otros sistemas operativos, guests Windows |

## Checkpoint

Creaste una VM con `kubectl apply` y encontraste su Pod y su proceso de QEMU. Lo que sigue: lo que haces con una VM todos los días.
