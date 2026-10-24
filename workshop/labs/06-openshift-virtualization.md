# Lab 6: OpenShift Virtualization (the product)

**Suggested time:** 60–90 minutes  
**Goal:** Install OpenShift Virtualization from the operator catalog, create a VM from the console catalog and with YAML, and see what the product adds on top of upstream KubeVirt.

OpenShift Virtualization (also called CNV) is Red Hat's supported build of KubeVirt and CDI. It is the same API you used in the session (`VirtualMachine`, `DataVolume`, `virtctl`), installed and upgraded by one operator, with a console UI, boot images, templates and Red Hat support.

> ⚠️ **Use a cluster without upstream KubeVirt.** The workshop clusters run upstream KubeVirt. Never install both on the same cluster. Either use another OpenShift cluster, or remove the upstream install first with `ansible-navigator run teardown.yml -e confirm_teardown=true` from the `ansible/` folder. The nodes must support virtualization (bare metal, or cloud instances with nested virtualization).

## Upstream KubeVirt or OpenShift Virtualization

| | Upstream KubeVirt | OpenShift Virtualization |
|---|---|---|
| Install and upgrade | Release YAML for KubeVirt and CDI, one at a time | One operator (HyperConverged) that installs KubeVirt, CDI, networking add-ons and templates, upgraded with OpenShift |
| UI | Third-party tools, such as kubevirt-manager in this workshop | **Virtualization** section in the OpenShift console |
| Boot images | You import them (`golden-image` in Module 4) | RHEL, CentOS Stream and Fedora images kept up to date automatically |
| VM sizes | You write CPU and memory in each VM | Instance types (`u1.small`, `u1.medium`...) and preferences per OS |
| Monitoring | Prometheus metrics | The same metrics plus dashboards and alerts |
| Support | Community | Red Hat, with a tested version for each OpenShift release |

## Install the operator

### From the console

1. Log in to the OpenShift console as a cluster admin.
2. Open **Operators**, **OperatorHub** (in newer consoles: **Ecosystem**, **Software Catalog**) and search for **OpenShift Virtualization**.
3. Click **Install**, keep the defaults (channel `stable`, namespace `openshift-cnv`) and click **Install** again.
4. When the operator shows **Succeeded**, click **Create HyperConverged**, keep the defaults and click **Create**.
5. Wait until the console shows the **Virtualization** section in the left menu (5 to 10 minutes).

### With YAML

The same steps as Kubernetes objects. OLM (the Operator Lifecycle Manager) reads the Subscription and installs the operator:

```bash
oc apply -f - <<'EOF'
apiVersion: v1
kind: Namespace
metadata:
  name: openshift-cnv
---
apiVersion: operators.coreos.com/v1
kind: OperatorGroup
metadata:
  name: kubevirt-hyperconverged-group
  namespace: openshift-cnv
spec:
  targetNamespaces:
    - openshift-cnv
---
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: hco-operatorhub
  namespace: openshift-cnv
spec:
  source: redhat-operators
  sourceNamespace: openshift-marketplace
  name: kubevirt-hyperconverged
  channel: stable
EOF
oc get csv -n openshift-cnv -w
```

Ctrl+C when the CSV phase is `Succeeded`. Then create the HyperConverged resource, the one object that configures the whole stack:

```bash
oc apply -f - <<'EOF'
apiVersion: hco.kubevirt.io/v1beta1
kind: HyperConverged
metadata:
  name: kubevirt-hyperconverged
  namespace: openshift-cnv
spec: {}
EOF
oc wait hco kubevirt-hyperconverged -n openshift-cnv --for=condition=Available --timeout=15m
```

Look at what it created:

```bash
oc get kubevirt,cdi,ssp,networkaddonsconfig -A
oc get pods -n openshift-cnv
```

The `KubeVirt` and `CDI` resources are the same ones you would create by hand with upstream. The operator owns them: change settings in the HyperConverged resource, not in them.

## Boot images and instance types

The product keeps a set of boot images ready in their own namespace:

```bash
oc get datasources -n openshift-virtualization-os-images
oc get dataimportcrons -n openshift-virtualization-os-images
```

A `DataImportCron` checks for a new image regularly and imports it; the `DataSource` always points to the latest one. This replaces the manual `golden-image` import from Module 4.

VM sizes come as instance types, like cloud flavors, and preferences set the right devices for each OS:

```bash
oc get virtualmachineclusterinstancetypes
oc get virtualmachineclusterpreferences
```

## Create a VM from the catalog

1. In the console, open **Virtualization**, **Catalog**.
2. On the **InstanceTypes** tab, under **Select volume to boot from**, click **fedora**.
3. Under **Select InstanceType**, choose **U series**, size **small** (`u1.small`).
4. Under **VirtualMachine details**, pick the project `demo-vms`, type the name `vm-catalog` and add your public SSH key.
5. Click **Create VirtualMachine**. The VM page opens and the VM starts.
6. Try the tabs: **Overview** (status and metrics), **Console** (VNC and serial in the browser), **Snapshots**, and the **Actions** menu (**Stop**, **Restart**, **Migrate**).

## The same VM in YAML

The catalog writes a normal `VirtualMachine`. This is the same VM by hand; note that it has no CPU, memory or disk bus, because the instance type and preference provide them:

```bash
oc apply -f - <<'EOF'
apiVersion: kubevirt.io/v1
kind: VirtualMachine
metadata:
  name: vm-catalog-yaml
  namespace: demo-vms
spec:
  runStrategy: Always
  instancetype:
    kind: VirtualMachineClusterInstancetype
    name: u1.small
  preference:
    kind: VirtualMachineClusterPreference
    name: fedora
  dataVolumeTemplates:
    - metadata:
        name: vm-catalog-yaml-rootdisk
      spec:
        sourceRef:
          kind: DataSource
          name: fedora
          namespace: openshift-virtualization-os-images
        storage:
          resources:
            requests:
              storage: 30Gi
  template:
    spec:
      domain:
        devices: {}
      accessCredentials:
        - sshPublicKey:
            source:
              secret:
                secretName: demo-ssh-key
            propagationMethod:
              noCloud: {}
      volumes:
        - name: rootdisk
          dataVolume:
            name: vm-catalog-yaml-rootdisk
        - name: cloudinit
          cloudInitNoCloud:
            userData: |
              #cloud-config
              hostname: vm-catalog-yaml
EOF
oc get vm,dv -n demo-vms vm-catalog-yaml
```

It uses the `demo-ssh-key` Secret from the session (Module 1); create it in your namespace if it is not there. Everything else from the session works unchanged: `virtctl ssh`, `virtctl migrate`, snapshots, Services and Ingress.

## Operators that complete the platform

| Operator | What it adds |
|---|---|
| Migration Toolkit for Virtualization (MTV) | Moves VMs in bulk from VMware vSphere, Red Hat Virtualization, OpenStack or OVA files |
| Kubernetes NMState | Bridges, bonds and VLANs on the nodes, for VMs on existing networks (Multus) |
| OpenShift Data Foundation | Ceph storage with Block/RWX volumes and snapshots, needed for live migration and fast clones |
| Node Health Check, Self Node Remediation, Fence Agents Remediation | Restart the VMs of a failed node on another node |
| Kube Descheduler | Rebalances running VMs across nodes with live migration |

## OpenShift Virtualization with this repo

The automation in `ansible/` supports both layers. With `virt_mode: cnv` it keeps OpenShift Virtualization and only adds what the workshop needs (kubevirt-manager, branding, demo VMs):

```bash
cd ~/txlf/ansible
ansible-navigator run site.yml -e virt_mode=cnv
```

See the "Virtualization mode" section of `ansible/README.md` for the differences.

## Cleanup

```bash
oc delete vm -n demo-vms vm-catalog vm-catalog-yaml
```

To uninstall the product: delete the HyperConverged resource first and wait until it is gone, then the Subscription, the CSV and the `openshift-cnv` namespace. Deleting the namespace first leaves the cluster stuck.
