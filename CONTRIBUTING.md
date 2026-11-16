# Contributing

Thanks for helping improve **KubeVirt Without Fear**, the Texas Linux Fest 2026 hands-on workshop. This repository holds the workshop site, the labs, and the Ansible automation that prepares the clusters.

## Repository layout

| Path | Contents |
| --- | --- |
| `workshop/` | Visual site (English and Spanish), agenda, prerequisites, labs 0–5 and manifests |
| `ansible/` | Cluster preparation: upstream KubeVirt and CDI (or OpenShift Virtualization with `virt_mode: cnv`), kubevirt-manager, TXLF branding and demo VMs |
| `.github/` | GitHub configuration |

## Making changes

1. Fork the repository and create a topic branch from `main`.
2. Keep changes focused: workshop content in `workshop/`, automation in `ansible/`.
3. The workshop is bilingual — if you change the English site or labs, mirror the change in the Spanish version (`index.es.html`, `prerequisites.es.md`, and the `*.es.js` files), or note in the pull request that the translation is pending.
4. Open a pull request against `main` describing what changed and, for lab changes, how you validated them.

## Ansible changes

- Follow the existing style: the rules in `ansible/.ansible-lint` and `ansible/.yamllint` apply.
- Playbooks run with ansible-navigator using `ansible/execution-environment.yml`; keep `ansible/requirements.yml` and `ansible/requirements.txt` up to date if you add dependencies.
- Never install upstream KubeVirt and OpenShift Virtualization on the same cluster — pick the path with `virt_mode` (`kubevirt` or `cnv`).

## Assets

- PNGs used in the workshop have transparent backgrounds; see `workshop/assets/README.md` for credits and details.
