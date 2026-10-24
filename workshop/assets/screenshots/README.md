# Screenshots for the session modules

The modules reference these files. Until a file exists, the workshop site hides its slot (GitHub shows a broken image).

Capture at about 1280 x 800, PNG, with the light console theme. Crop out the browser chrome and anything with a password or token.

| File | Module | What to show | How to get there |
|---|---|---|---|
| `console-web-terminal.png` | 1 | OpenShift console with the web terminal open at the bottom and a prompt | Console, `>_` icon in the top bar, **Start** |
| `landing-vm-web.png` | 1 | The vm-web landing page with the node name | `https://vm-web.apps.<cluster domain>` |
| `kvm-dashboard.png` | 1 | kubevirt-manager Dashboard after signing in | `https://kubevirt-manager.apps.<cluster domain>` |
| `kvm-vm-list.png` | 3 | The **Virtual Machines** list with the demo VMs | kubevirt-manager, left menu **Virtual Machines** |
| `kvm-vm-details.png` | 3 | The `vm-live` page: action buttons (top right) and the tabs | **Virtual Machines**, click **vm-live** |
| `kvm-disks.png` | 4 | **Disks** tab of `vm-clone-live`, source `pvc (demo-vms - golden-image)` | **Virtual Machines**, **vm-clone-live**, **Disks** |
| `kvm-networking.png` | 5 | **Networking** tab of `vm-web`: NIC `default`, `podNetwork`, `masquerade`, IP | **Virtual Machines**, **vm-web**, **Networking** |
| `console-metrics.png` | 6 | **Observe, Metrics** with `rate(kubevirt_vmi_vcpu_seconds_total{namespace="demo-vms"}[2m])` and its graph | Console, **Observe**, **Metrics**, paste the query, **Run queries** |
| `kvm-monitoring.png` | 6 | **Monitoring** tab of `vm-web` with the CPU/memory/network/storage graphs | **Virtual Machines**, **vm-web**, **Monitoring** |

`vm-live` and `vm-clone-live` exist only after a participant runs Modules 2 and 4 (`kubectl apply -f manifests/01-vm-live.yaml` and `02-vm-clone-live.yaml`); `reset.yml` removes them.
