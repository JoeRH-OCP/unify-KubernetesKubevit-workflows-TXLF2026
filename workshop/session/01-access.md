# Module 1: Get access from your browser

**Time:** 5 minutes
**Goal:** Log in to your own OpenShift cluster and open a terminal, all inside the browser. Nothing to install, any operating system works.

Each person or pair gets a dedicated cluster that the instructor prepared before the session. It already runs KubeVirt and CDI, a Fedora golden image, five demo VMs and the kubevirt-manager UI. You have cluster-admin, so nothing you do affects other participants.

## Pick your lab

The instructor shares a Google Sheet with one row per lab cluster (the link is on the screen and in the session chat). Each row has:

- **Console URL:** `https://console-openshift-console.apps.<cluster>.<domain>`
- **User:** `admin`
- **Password:** a random password for that cluster (kubevirt-manager uses the same one)

Pick a row that nobody has taken and write your name in it, in the column the instructor points out. That cluster is yours for the whole session; do not use a row with someone else's name.

## Open the web terminal

1. Open the console URL and log in as `admin`.
2. Click the terminal icon (`>_`) in the top bar, then **Start**.
3. Wait until the prompt appears: `oc` and `kubectl` are already logged in to your cluster.

The terminal runs in a Pod in your cluster, so all commands in this workshop work the same from Windows, macOS, Linux or a Chromebook.

## Get the lab files

Run everything from here on **in the web terminal**: it is a Linux container in your cluster, so nothing is installed on your laptop.

Clone the workshop repository; all the manifests you need are in `ansible/manifests`:

```bash
git clone https://github.com/JoeRH-OCP/unify-KubernetesKubevit-workflows-TXLF2026.git ~/txlf
cd ~/txlf/ansible
ls manifests
```

No `git` in your terminal? Download the same files as an archive instead:

```bash
mkdir -p ~/txlf && curl -fsSL https://github.com/JoeRH-OCP/unify-KubernetesKubevit-workflows-TXLF2026/archive/refs/heads/main.tar.gz | tar -xz --strip-components=1 -C ~/txlf
cd ~/txlf/ansible
```

## Get virtctl

> ⚠️ **Run this in the OpenShift web terminal, not on your laptop.** It downloads `virtctl` into the web terminal's container; nothing is installed on your computer.

`virtctl` is the KubeVirt command line tool (console, SSH, start, stop, migrate). It must match the KubeVirt version in the cluster (v1.9.1):

```bash
mkdir -p ~/bin && export PATH=~/bin:$PATH
curl -fsSL -o ~/bin/virtctl https://github.com/kubevirt/kubevirt/releases/download/v1.9.1/virtctl-v1.9.1-linux-amd64
chmod +x ~/bin/virtctl
virtctl version
```

## Create your SSH key

```bash
test -f ~/.ssh/id_ed25519 || ssh-keygen -t ed25519 -N '' -f ~/.ssh/id_ed25519
./manifests/00-ssh-key.sh
```

The script stores your public key in a Secret. KubeVirt injects it into the VMs you create, so `virtctl ssh` works without passwords.

## Find your URLs

```bash
kubectl get ingress -A -o 'custom-columns=NAMESPACE:.metadata.namespace,HOST:.spec.rules[0].host'
```

Open both in new browser tabs:

- `https://vm-web.apps...`: a web page served from inside a VM. It shows which Kubernetes node runs the VM and refreshes every 2 seconds. Keep it open; you will watch it in Module 6.
- `https://kubevirt-manager.apps...`: a web UI for KubeVirt. Log in with `admin` and your password.

## Optional: use your own laptop

You do not need this: the web terminal has everything. If you prefer your own terminal, you need `oc` (or `kubectl`), `virtctl` v1.9.1 and `git`. Get `oc` from your cluster's console: **?** (help menu) > **Command Line Tools**. The lab commands are bash; zsh on macOS works too.

macOS or Linux:

```bash
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m | sed 's/x86_64/amd64/;s/aarch64/arm64/')
curl -fsSL -o virtctl "https://github.com/kubevirt/kubevirt/releases/download/v1.9.1/virtctl-v1.9.1-${OS}-${ARCH}"
chmod +x virtctl && sudo mv virtctl /usr/local/bin/
virtctl version --client
```

Windows: the lab commands use bash features (pipes, `$(...)`, heredocs), so run them in WSL (Ubuntu) and follow the Linux steps above. If you only want `virtctl` in PowerShell (for consoles, SSH, start and stop):

```powershell
Invoke-WebRequest -Uri https://github.com/kubevirt/kubevirt/releases/download/v1.9.1/virtctl-v1.9.1-windows-amd64.exe -OutFile virtctl.exe
.\virtctl.exe version --client
```

Then log in with the API URL of your cluster (console user menu, **Copy login command**), clone the repository as in "Get the lab files", and run the same commands:

```bash
oc login --server=https://api.<cluster>.<domain>:6443 -u admin
```

## Checkpoint

```bash
kubectl get vm -n demo-vms
```

You should see `vm-quick`, `vm-web` and `vm-clone-1` to `vm-clone-3`, all `Running`. If not, raise your hand now: the next modules depend on it.

> The web terminal resets after a period of inactivity. If `virtctl` disappears, run the "Get virtctl" commands again.
