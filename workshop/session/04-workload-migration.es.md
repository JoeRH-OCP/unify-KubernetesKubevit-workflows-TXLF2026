# Módulo 4: Migración unificada de cargas de trabajo

**Tiempo:** 30 minutos
**Objetivo:** Mueve una VM en ejecución entre nodos sin downtime, protégela con un snapshot, recupérala después de un error y ve cómo las VMs existentes se migran a Kubernetes.

Mantén abierta, donde puedas verla, la página de `vm-web` del Módulo 1.

## Parte A: migración en vivo (10 minutos)

`vm-web` ejecuta nginx dentro de una VM Fedora. Cada 2 segundos la página le pregunta al cluster qué nodo ejecuta la VM.

```bash
kubectl get vmi -n demo-vms vm-web -o wide
```

Anota el `NODENAME`. Ahora mueve la VM en ejecución:

```bash
virtctl migrate vm-web -n demo-vms
kubectl get vmim -n demo-vms -w
```

Observa el navegador mientras corre la migración: la página muestra "Live migration in progress" y luego el nombre del nuevo nodo parpadea en naranja. La página nunca se recarga y nginx sigue respondiendo.

Presiona Ctrl+C cuando la migración muestre `Succeeded` y luego confirma:

```bash
kubectl get vmi -n demo-vms vm-web -o wide
```

Lo que pasó por debajo:

1. KubeVirt inició un segundo Pod `virt-launcher` en otro nodo.
2. QEMU copió la memoria del guest a ese Pod mientras la VM seguía corriendo y luego hizo el cambio en milisegundos.
3. El disco no se movió: es un volumen Block/RWX, así que ambos nodos podían abrirlo.
4. El Service de Kubernetes sigue al nuevo Pod, así que la URL sigue funcionando.

```bash
kubectl get pods -n demo-vms -l vm.kubevirt.io/name=vm-web -o wide
```

El Pod anterior está en `Completed`; el nuevo está en `Running`.

## Parte B: el mantenimiento de nodos mueve las VMs por ti (5 minutos)

Cuando un nodo necesita parches, no migras las VMs a mano. El spec de la VM indica qué hacer cuando se hace drain de su nodo:

```bash
kubectl get vm vm-web -n demo-vms -o jsonpath='{.spec.template.spec.evictionStrategy}{"\n"}'
```

`LiveMigrate` significa "si hacen drain de mi nodo, mígrenme, no me maten". Pruébalo de forma segura con un cordon:

```bash
NODE=$(kubectl get vmi -n demo-vms vm-web -o jsonpath='{.status.nodeName}')
kubectl cordon $NODE
virtctl migrate vm-web -n demo-vms
kubectl get vmi -n demo-vms vm-web -o wide -w
```

Ctrl+C cuando cambie el nodo. El nodo con cordon no acepta Pods nuevos, así que la VM se fue a otro nodo. Siempre deshaz el cordon:

```bash
kubectl uncordon $NODE
```

Con `kubectl drain`, cada VM con `evictionStrategy: LiveMigrate` en ese nodo se migraría de la misma forma. El resto de los Pods del nodo se reprograman como siempre. Un solo conjunto de reglas para contenedores y VMs.

## Parte C: snapshot, romper, restaurar (10 minutos)

Usa `vm-clone-live`, la VM que creaste en el Módulo 3 con tu llave SSH. Primero, guarda algunos "datos importantes" en ella:

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

Ctrl+C cuando `READYTOUSE` sea `true`. El QEMU guest agent congeló los sistemas de archivos del guest para que el snapshot sea consistente, y Ceph tomó un snapshot CSI del disco.

Ahora, el error:

```bash
virtctl ssh fedora@vm/vm-clone-live -n demo-vms -c 'sudo rm -f /srv/data.txt; ls -l /srv'
```

El archivo desapareció. Restaura la VM. Debe estar detenida para restaurar sus discos:

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

Ctrl+C cuando `COMPLETE` sea `true`; luego inicia la VM y revisa el archivo:

```bash
virtctl start vm-clone-live -n demo-vms
kubectl wait vmi/vm-clone-live -n demo-vms --for=condition=AgentConnected --timeout=180s
virtctl ssh fedora@vm/vm-clone-live -n demo-vms -c 'cat /srv/data.txt'
```

Los datos regresaron, exactamente como estaban cuando tomaste el snapshot.

> El instructor muestra el mismo flujo en `vm-web` con la página web: rompe el sitio, lo restaura y puedes ver cómo vuelve (`ansible/manifests/04-snapshot.yaml` y `05-restore.yaml`).

## Parte D: migrar VMs a Kubernetes (5 minutos, discusión)

Hasta ahora las VMs nacieron en el cluster. La mayoría de las organizaciones empiezan con VMs en otro hipervisor. Tres formas de traerlas:

| Ruta | Qué hace | Ideal para |
|---|---|---|
| Importación de discos con CDI | Un `DataVolume` importa una imagen qcow2/raw desde HTTP, S3, un registry o una subida (así se creó `golden-image`) | VMs individuales, golden images, appliances |
| Migration Toolkit for Virtualization (Forklift) | Planea y ejecuta migraciones desde VMware vSphere, oVirt/RHV, OpenStack u OVA, convierte drivers y mapea redes/almacenamiento | Flotas de VMs, ventanas de cutover |
| Reconstruir como contenedores | Saca la aplicación de la VM cuando tenga sentido | Servicios stateless, versiones nuevas |

El sentido de "unificada": una vez que la VM está adentro, se programa, se conecta a la red, se almacena, se monitorea, se migra y se respalda con las mismas herramientas de Kubernetes que tus contenedores. Puedes mover cada carga de trabajo a un contenedor después, una por una, o nunca.

## Checkpoint

Hiciste la migración en vivo de una VM sin downtime, usaste las reglas de mantenimiento de nodos, restauraste una VM desde un snapshot y conoces las rutas para traer VMs al cluster.
