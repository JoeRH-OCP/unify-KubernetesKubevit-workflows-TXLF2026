# Módulo 1: Accede desde tu navegador

**Tiempo:** 5 minutos
**Objetivo:** Inicia sesión en tu propio cluster de OpenShift y abre una terminal, todo dentro del navegador. No hay nada que instalar y funciona con cualquier sistema operativo.

Cada persona o pareja recibe un cluster dedicado que el instructor preparó antes de la sesión. Ya tiene KubeVirt y CDI, una golden image de Fedora, cinco VMs de demo y la interfaz kubevirt-manager. Tienes cluster-admin, así que nada de lo que hagas afecta a otros participantes.

## Elige tu lab

El instructor comparte una hoja de Google Sheets con un renglón por cada cluster de laboratorio (el link está en la pantalla y en el chat de la sesión). Cada renglón tiene:

- **URL de la consola:** `https://console-openshift-console.apps.<cluster>.<domain>`
- **Usuario:** `admin`
- **Contraseña:** una contraseña aleatoria para ese cluster (kubevirt-manager usa la misma)

Elige un renglón que nadie haya tomado y escribe tu nombre en él, en la columna que indique el instructor. Ese cluster es tuyo durante toda la sesión; no uses un renglón que ya tenga el nombre de otra persona.

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

## Obtén virtctl

> ⚠️ **Ejecuta esto en la terminal web de OpenShift, no en tu laptop.** Descarga `virtctl` dentro del contenedor de la terminal web; no se instala nada en tu computadora.

`virtctl` es la herramienta de línea de comandos de KubeVirt (consola, SSH, start, stop, migrate). Debe coincidir con la versión de KubeVirt del cluster (v1.9.1):

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
kubectl get ingress -A -o 'custom-columns=NAMESPACE:.metadata.namespace,HOST:.spec.rules[0].host'
```

Abre ambas en pestañas nuevas del navegador:

- `https://vm-web.apps...`: una página web servida desde dentro de una VM. Muestra qué nodo de Kubernetes ejecuta la VM y se actualiza cada 2 segundos. Déjala abierta; la vas a observar en el Módulo 6.
- `https://kubevirt-manager.apps...`: una interfaz web para KubeVirt. Inicia sesión con `admin` y tu contraseña.

## Opcional: usa tu propia laptop

No lo necesitas: la terminal web tiene todo. Si prefieres tu propia terminal, necesitas `oc` (o `kubectl`), `virtctl` v1.9.1 y `git`. Obtén `oc` desde la consola de tu cluster: **?** (menú de ayuda) > **Command Line Tools**. Los comandos del laboratorio son de bash; zsh en macOS también funciona.

macOS o Linux:

```bash
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m | sed 's/x86_64/amd64/;s/aarch64/arm64/')
curl -fsSL -o virtctl "https://github.com/kubevirt/kubevirt/releases/download/v1.9.1/virtctl-v1.9.1-${OS}-${ARCH}"
chmod +x virtctl && sudo mv virtctl /usr/local/bin/
virtctl version --client
```

Windows: los comandos del laboratorio usan funciones de bash (pipes, `$(...)`, heredocs), así que córrelos en WSL (Ubuntu) y sigue los pasos de Linux de arriba. Si solo quieres `virtctl` en PowerShell (para consolas, SSH, start y stop):

```powershell
Invoke-WebRequest -Uri https://github.com/kubevirt/kubevirt/releases/download/v1.9.1/virtctl-v1.9.1-windows-amd64.exe -OutFile virtctl.exe
.\virtctl.exe version --client
```

Después inicia sesión con la URL de la API de tu cluster (menú de usuario de la consola, **Copy login command**), clona el repositorio como en "Obtén los archivos del laboratorio" y ejecuta los mismos comandos:

```bash
oc login --server=https://api.<cluster>.<domain>:6443 -u admin
```

## Checkpoint

```bash
kubectl get vm -n demo-vms
```

Deberías ver `vm-quick`, `vm-web` y de `vm-clone-1` a `vm-clone-3`, todas en `Running`. Si no, levanta la mano ahora: los siguientes módulos dependen de esto.

> La terminal web se reinicia después de un periodo de inactividad. Si `virtctl` desaparece, vuelve a ejecutar los comandos de "Obtén virtctl".
