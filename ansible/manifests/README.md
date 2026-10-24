# Hand-written manifests for the live demo

These files are **not** used by Ansible. Run them from the `ansible/` folder
(`kubectl apply -f manifests/...`). They exist so you can show plain
`kubectl apply` on stage. They assume the defaults from `../group_vars/all/`
(namespace `demo-vms`, StorageClass `ocs-external-storagecluster-ceph-rbd`,
`golden-image` already imported). Edit them if your infra.yml differs.

| File | What it shows |
|---|---|
| 00-ssh-key.sh | Puts your SSH public key in a Secret (used by 01 and 02) |
| 01-vm-live.yaml | VM from a containerDisk, SSH key injected by KubeVirt |
| 02-vm-clone-live.yaml | VM whose disk is a snapshot clone of golden-image |
| 03-migration.yaml | Live migration of vm-web |
| 04-snapshot.yaml | VirtualMachineSnapshot of vm-web |
| 05-restore.yaml | Restore vm-web from that snapshot (stop the VM first) |
| 06-vm-secondary-net.yaml | VM with a second NIC on the Linux bridge (optional) |
