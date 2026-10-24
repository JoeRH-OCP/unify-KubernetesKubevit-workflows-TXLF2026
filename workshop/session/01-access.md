# Module 1: Get access from your browser

**Time:** 5 minutes
**Goal:** Log in to your own OpenShift cluster and open a terminal, all inside the browser. Nothing to install, any operating system works.

Each person or pair has a dedicated cluster that the instructor prepared before the session. It already runs KubeVirt and CDI, a Fedora golden image, five demo VMs and the kubevirt-manager UI. You have cluster-admin, so nothing you do affects other participants.

## What you received

Your handout card has:

- **Console URL:** `https://console-openshift-console.apps.<cluster>.<domain>`
- **User:** `admin`
- **Password:** a random password for your cluster (kubevirt-manager uses the same one)

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

## Get virtctl (in the web terminal)

`virtctl` is the KubeVirt command line tool (console, SSH, start, stop, migrate). It must match the KubeVirt version in the cluster (v1.9.1). This downloads it into the web terminal, not onto your laptop:

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
kubectl get ingress -A -o custom-columns=NAMESPACE:.metadata.namespace,HOST:.spec.rules[0].host
```

Open both in new browser tabs:

- `https://vm-web.apps...`: a web page served from inside a VM. It shows which Kubernetes node runs the VM and refreshes every 2 seconds. Keep it open; you will watch it in Module 6.
- `https://kubevirt-manager.apps...`: a web UI for KubeVirt. Log in with `admin` and your password.

## Optional: use your own laptop

You do not need this for the workshop. If you prefer your own terminal, install `oc` (or `kubectl`) and the `virtctl` build for your OS from the [KubeVirt v1.9.1 release](https://github.com/kubevirt/kubevirt/releases/tag/v1.9.1):

| Your OS | virtctl file |
|---|---|
| macOS, Apple silicon | `virtctl-v1.9.1-darwin-arm64` |
| macOS, Intel | `virtctl-v1.9.1-darwin-amd64` |
| Linux | `virtctl-v1.9.1-linux-amd64` |
| Windows | `virtctl-v1.9.1-windows-amd64.exe` |

Then log in with the API URL from the console (user menu, **Copy login command**), clone the repository, and run the same commands:

```bash
oc login --server=https://api.<cluster>.<domain>:6443 -u admin
```

## Checkpoint

```bash
kubectl get vm -n demo-vms
```

You should see `vm-quick`, `vm-web` and `vm-clone-1` to `vm-clone-3`, all `Running`. If not, raise your hand now: the next modules depend on it.

> The web terminal resets after a period of inactivity. If `virtctl` disappears, run the "Get virtctl (in the web terminal)" commands again.
