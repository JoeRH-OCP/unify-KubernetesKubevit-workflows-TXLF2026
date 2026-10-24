# Módulo 1: Accede a tu cluster

**Tiempo:** 5 minutos
**Objetivo:** Inicia sesión en tu propio cluster de OpenShift, deja funcionando `kubectl` y `virtctl`, y abre las tres URLs que vas a usar hoy.

Cada persona o pareja tiene un cluster dedicado que el instructor preparó antes de la sesión. Ya ejecuta KubeVirt y CDI upstream, una golden image de Fedora, cinco VMs de demo y la interfaz kubevirt-manager. Tienes cluster-admin, así que nada de lo que hagas afecta a otros participantes.

## Lo que recibiste

Tu tarjeta tiene:

- **Console URL:** `https://console-openshift-console.apps.<cluster>.<domain>`
- **Usuario:** `admin`
- **Contraseña:** una contraseña aleatoria para tu cluster (kubevirt-manager usa la misma)

## Opción A: terminal web de OpenShift (no hay que instalar nada)

1. Abre la URL de la consola e inicia sesión como `admin`.
2. Haz clic en el ícono de terminal (`>_`) en la barra superior y luego en **Start**.
3. Espera a que aparezca el prompt; `oc` y `kubectl` ya tienen la sesión iniciada.

## Opción B: tu laptop

Usa la URL de la API que aparece en la consola (menú de usuario, **Copy login command**) y ejecuta:

```bash
oc login --server=https://api.<cluster>.<domain>:6443 -u admin
```

## Consigue virtctl

`virtctl` es el CLI de KubeVirt (console, SSH, migrate, start, stop). Debe coincidir con la versión de KubeVirt del cluster (v1.9.1):

```bash
virtctl version --client || {
  mkdir -p ~/bin
  curl -fsSL -o ~/bin/virtctl https://github.com/kubevirt/kubevirt/releases/download/v1.9.1/virtctl-v1.9.1-linux-amd64
  chmod +x ~/bin/virtctl
  export PATH=~/bin:$PATH
}
virtctl version
```

En una Mac, usa `virtctl-v1.9.1-darwin-arm64` (Apple silicon) o `virtctl-v1.9.1-darwin-amd64`.

## Consigue los archivos del laboratorio y una llave SSH

```bash
git clone https://github.com/JoeRH-OCP/unify-KubernetesKubevit-workflows-TXLF2026.git
cd unify-KubernetesKubevit-workflows-TXLF2026/ansible
test -f ~/.ssh/id_ed25519 || ssh-keygen -t ed25519 -N '' -f ~/.ssh/id_ed25519
./manifests/00-ssh-key.sh
```

El último comando guarda tu llave pública en un Secret. KubeVirt la inyecta en las VMs que crees, así que `virtctl ssh` funciona sin contraseñas.

¿No tienes `git`? Descarga solo los archivos que necesitas:

```bash
mkdir -p ~/txlf/manifests && cd ~/txlf
for f in 00-ssh-key.sh 01-vm-live.yaml 02-vm-clone-live.yaml; do
  curl -fsSL -o manifests/$f https://raw.githubusercontent.com/JoeRH-OCP/unify-KubernetesKubevit-workflows-TXLF2026/main/ansible/manifests/$f
done
chmod +x manifests/00-ssh-key.sh
```

## Encuentra tus URLs

```bash
kubectl get ingress -A -o custom-columns=NAMESPACE:.metadata.namespace,HOST:.spec.rules[0].host
```

Abre ambas en pestañas nuevas del navegador:

- `https://vm-web.apps...`: una página web servida desde dentro de una VM. Muestra qué nodo de Kubernetes ejecuta la VM y se actualiza cada 2 segundos. Tenla a la vista; es la estrella del Módulo 4.
- `https://kubevirt-manager.apps...`: una interfaz web para KubeVirt. Inicia sesión con `admin` y tu contraseña.

## Checkpoint

```bash
kubectl get vm -n demo-vms
```

Debes ver `vm-quick`, `vm-web` y de `vm-clone-1` a `vm-clone-3`, todas en `Running`. Si no, levanta la mano ahora: los siguientes módulos dependen de esto.
