# Módulo 1: Accede desde tu navegador

**Tiempo:** 5 minutos
**Objetivo:** Inicia sesión en tu propio cluster de OpenShift y abre una terminal, todo dentro del navegador. No hay nada que instalar y funciona con cualquier sistema operativo.

Cada persona o pareja tiene un cluster dedicado que el instructor preparó antes de la sesión. Ya tiene KubeVirt y CDI, una golden image de Fedora, cinco VMs de demo y la interfaz kubevirt-manager. Tienes cluster-admin, así que nada de lo que hagas afecta a otros participantes.

## Lo que recibiste

Tu tarjeta incluye:

- **URL de la consola:** `https://console-openshift-console.apps.<cluster>.<domain>`
- **Usuario:** `admin`
- **Contraseña:** una contraseña aleatoria para tu cluster (kubevirt-manager usa la misma)

## Abre la terminal web

1. Abre la URL de la consola e inicia sesión como `admin`.
2. Haz clic en el ícono de terminal (`>_`) en la barra superior y luego en **Start**.
3. Espera a que aparezca el prompt: `oc` y `kubectl` ya tienen sesión iniciada en tu cluster.

La terminal corre en un Pod dentro de tu cluster, así que todos los comandos de este workshop funcionan igual desde Windows, macOS, Linux o una Chromebook.

## Obtén virtctl

`virtctl` es la herramienta de línea de comandos de KubeVirt (consola, SSH, start, stop, migrate). Debe coincidir con la versión de KubeVirt del cluster (v1.9.1):

```bash
mkdir -p ~/bin && export PATH=~/bin:$PATH
curl -fsSL -o ~/bin/virtctl https://github.com/kubevirt/kubevirt/releases/download/v1.9.1/virtctl-v1.9.1-linux-amd64
chmod +x ~/bin/virtctl
virtctl version
```

## Obtén los archivos del laboratorio y una clave SSH

```bash
mkdir -p ~/txlf/manifests && cd ~/txlf
for f in 00-ssh-key.sh 01-vm-live.yaml 02-vm-clone-live.yaml; do
  curl -fsSL -o manifests/$f https://raw.githubusercontent.com/JoeRH-OCP/unify-KubernetesKubevit-workflows-TXLF2026/main/ansible/manifests/$f
done
chmod +x manifests/00-ssh-key.sh
test -f ~/.ssh/id_ed25519 || ssh-keygen -t ed25519 -N '' -f ~/.ssh/id_ed25519
./manifests/00-ssh-key.sh
```

El último comando guarda tu clave pública en un Secret. KubeVirt la inyecta en las VMs que crees, así que `virtctl ssh` funciona sin contraseñas.

## Encuentra tus URLs

```bash
kubectl get ingress -A -o custom-columns=NAMESPACE:.metadata.namespace,HOST:.spec.rules[0].host
```

Abre ambas en pestañas nuevas del navegador:

- `https://vm-web.apps...`: una página web servida desde dentro de una VM. Muestra qué nodo de Kubernetes ejecuta la VM y se actualiza cada 2 segundos. Déjala abierta; la vas a observar en el Módulo 6.
- `https://kubevirt-manager.apps...`: una interfaz web para KubeVirt. Inicia sesión con `admin` y tu contraseña.

## Checkpoint

```bash
kubectl get vm -n demo-vms
```

Deberías ver `vm-quick`, `vm-web` y de `vm-clone-1` a `vm-clone-3`, todas en `Running`. Si no, levanta la mano ahora: los siguientes módulos dependen de esto.

> La terminal web se reinicia después de un periodo de inactividad. Si `virtctl` desaparece, vuelve a ejecutar los comandos de "Obtén virtctl".
