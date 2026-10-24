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

## Obtén los archivos del laboratorio

Ejecuta todo a partir de aquí **en la terminal web**: es un contenedor Linux dentro de tu cluster, así que no se instala nada en tu laptop.

Clona el repositorio del workshop; todos los manifests que necesitas están en `ansible/manifests`:

```bash
git clone https://github.com/JoeRH-OCP/unify-KubernetesKubevit-workflows-TXLF2026.git ~/txlf
cd ~/txlf/ansible
ls manifests
```

¿Tu terminal no tiene `git`? Descarga los mismos archivos como un archivo comprimido:

```bash
mkdir -p ~/txlf && curl -fsSL https://github.com/JoeRH-OCP/unify-KubernetesKubevit-workflows-TXLF2026/archive/refs/heads/main.tar.gz | tar -xz --strip-components=1 -C ~/txlf
cd ~/txlf/ansible
```

## Obtén virtctl (en la terminal web)

`virtctl` es la herramienta de línea de comandos de KubeVirt (consola, SSH, start, stop, migrate). Debe coincidir con la versión de KubeVirt del cluster (v1.9.1). Esto la descarga en la terminal web, no en tu laptop:

```bash
mkdir -p ~/bin && export PATH=~/bin:$PATH
curl -fsSL -o ~/bin/virtctl https://github.com/kubevirt/kubevirt/releases/download/v1.9.1/virtctl-v1.9.1-linux-amd64
chmod +x ~/bin/virtctl
virtctl version
```

## Crea tu llave SSH

```bash
test -f ~/.ssh/id_ed25519 || ssh-keygen -t ed25519 -N '' -f ~/.ssh/id_ed25519
./manifests/00-ssh-key.sh
```

El script guarda tu llave pública en un Secret. KubeVirt la inyecta en las VMs que crees, así que `virtctl ssh` funciona sin contraseñas.

## Encuentra tus URLs

```bash
kubectl get ingress -A -o custom-columns=NAMESPACE:.metadata.namespace,HOST:.spec.rules[0].host
```

Abre ambas en pestañas nuevas del navegador:

- `https://vm-web.apps...`: una página web servida desde dentro de una VM. Muestra qué nodo de Kubernetes ejecuta la VM y se actualiza cada 2 segundos. Déjala abierta; la vas a observar en el Módulo 6.
- `https://kubevirt-manager.apps...`: una interfaz web para KubeVirt. Inicia sesión con `admin` y tu contraseña.

## Opcional: usa tu propia laptop

No lo necesitas para el workshop. Si prefieres tu propia terminal, instala `oc` (o `kubectl`) y el `virtctl` para tu sistema operativo desde el [release v1.9.1 de KubeVirt](https://github.com/kubevirt/kubevirt/releases/tag/v1.9.1):

| Tu sistema operativo | Archivo de virtctl |
|---|---|
| macOS, Apple silicon | `virtctl-v1.9.1-darwin-arm64` |
| macOS, Intel | `virtctl-v1.9.1-darwin-amd64` |
| Linux | `virtctl-v1.9.1-linux-amd64` |
| Windows | `virtctl-v1.9.1-windows-amd64.exe` |

Después inicia sesión con la URL de la API que muestra la consola (menú de usuario, **Copy login command**), clona el repositorio y ejecuta los mismos comandos:

```bash
oc login --server=https://api.<cluster>.<domain>:6443 -u admin
```

## Checkpoint

```bash
kubectl get vm -n demo-vms
```

Deberías ver `vm-quick`, `vm-web` y de `vm-clone-1` a `vm-clone-3`, todas en `Running`. Si no, levanta la mano ahora: los siguientes módulos dependen de esto.

> La terminal web se reinicia después de un periodo de inactividad. Si `virtctl` desaparece, vuelve a ejecutar los comandos de "Obtén virtctl (en la terminal web)".
