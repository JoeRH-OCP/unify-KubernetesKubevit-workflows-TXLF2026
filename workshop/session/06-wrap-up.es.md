# Módulo 6: Cierre y siguientes pasos

**Tiempo:** 10 minutos (incluye preguntas)

## Lo que hiciste en 90 minutos

| Módulo | Viste que |
|---|---|
| 2. Una VM es un Pod | KubeVirt agrega objetos de VM a la API de Kubernetes; cada VM en ejecución es un Pod `virt-launcher` con QEMU adentro |
| 3. Los discos son PVCs | CDI importa las imágenes; los clones son snapshots CSI, listos en segundos |
| 4. Migración de cargas de trabajo | Las VMs en ejecución se mueven entre nodos sin downtime, siguen las reglas de mantenimiento de nodos y se recuperan desde snapshots; las VMs existentes entran a través de CDI o MTV |
| 5. Expón y observa | Las VMs usan los mismos Services, Ingress, métricas y eventos que los contenedores |

Todo corrió sobre proyectos upstream con APIs estándar de Kubernetes: KubeVirt v1.9.1, CDI v1.66.1, kubevirt-manager, Ceph RBD vía CSI.

## ¿Contenedores o VMs?

| Elige un contenedor cuando | Elige una VM cuando |
|---|---|
| La aplicación ya está empaquetada como imagen | La aplicación necesita su propio kernel, módulos del kernel o un sistema operativo distinto |
| Quieres arranque rápido y alta densidad | Es un appliance de un proveedor o un sistema legacy que no puedes reconstruir |
| El escalamiento es horizontal | El software se licencia o certifica por VM |

En una sola plataforma no tienes que elegir para todo el data center: cada carga de trabajo puede moverse cuando esté lista.

## Hacia dónde seguir

- **Guía de usuario de KubeVirt:** https://kubevirt.io/user-guide/
- **Instance types y preferences:** tamaños de VM como los flavors de la nube (`kubectl get virtualmachineclusterinstancetypes`).
- **Migration Toolkit for Virtualization / Forklift:** migración masiva desde vSphere, oVirt y OpenStack.
- **GitOps para VMs:** las VMs son YAML, así que Argo CD o Flux pueden administrarlas.
- **Guests Windows, GPUs y SR-IOV:** en los extras autoguiados y en la documentación de KubeVirt.
- **Este workshop:** los extras autoguiados del menú profundizan en contenedores, redes y almacenamiento de Kubernetes.

## Preguntas

Tu cluster sigue disponible hasta que el instructor lo reinicie. Todo lo que está en `ansible/manifests/` y en estos módulos se puede repetir en cualquier cluster con KubeVirt y CDI.

Gracias por asistir a Texas Linux Fest 2026.
