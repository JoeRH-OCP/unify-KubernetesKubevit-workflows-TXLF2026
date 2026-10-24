# Módulo 7: Trade-offs y un solo plano de control

**Tiempo:** 10 minutos (incluye preguntas)

## Lo que hiciste en 90 minutos

| Módulo | Viste que |
|---|---|
| 2. Cómo funciona KubeVirt | Una VM es un objeto de Kubernetes; cada VM en ejecución es un Pod `virt-launcher` con KVM/QEMU dentro |
| 3. Ciclo de vida de la VM | SSH, consolas, iniciar, detener y reiniciar con `virtctl` y `runStrategy` |
| 4. Almacenamiento | Los discos son PVCs; CDI importa las imágenes; los clones son snapshots CSI |
| 5. Redes | Las VMs obtienen IPs de Pod, viven detrás de Services e Ingress y hablan con contenedores por DNS |
| 6. Operaciones de día 2 | Migración en vivo, mantenimiento de nodos, snapshot y restauración, métricas y eventos |

## Un solo plano de control

| Tarea | Stacks separados | Una plataforma con KubeVirt |
|---|---|---|
| Despliegue | Consola o scripts del hipervisor + YAML de Kubernetes | YAML y GitOps para ambos |
| Control de acceso | Dos modelos de RBAC, dos audit logs | RBAC y auditoría de Kubernetes para ambos |
| Redes | VLANs y port groups + Services e Ingress | Services, Ingress y NetworkPolicy para ambos |
| Almacenamiento | Datastores + StorageClasses | StorageClasses y snapshots para ambos |
| Monitoreo | Dos herramientas, dos dashboards | Prometheus y las mismas alertas para ambos |
| Parches de nodos | Dos procedimientos de mantenimiento | `kubectl drain` mueve VMs y reprograma contenedores |

## Los trade-offs honestos

| Considera | Por qué importa |
|---|---|
| Almacenamiento | La migración en vivo necesita almacenamiento block RWX (Ceph, NFS con cuidado, muchos drivers CSI de SAN). Revisa primero tu driver CSI. |
| Habilidades | Los administradores de VMs necesitan bases de Kubernetes (Pods, Services, YAML); los equipos de plataforma necesitan bases de VMs (sistema operativo del guest, consolas, dimensionamiento). |
| Overhead | Cada VM es un Pod más QEMU: un pequeño overhead de memoria por VM; planea la capacidad considerándolo. |
| Paridad de funciones | La mayoría de las funciones del día a día existen; algunas funciones específicas del hipervisor (por ejemplo, algunas herramientas del fabricante) tienen equivalentes distintos o no tienen. |
| Soporte y licenciamiento | KubeVirt upstream tiene soporte de la comunidad; las distribuciones de los fabricantes agregan soporte. Revisa el licenciamiento del sistema operativo del guest y de las apps por VM. |
| Esfuerzo de migración | Traer VMs requiere planeación: importación de discos con CDI para VMs individuales, Migration Toolkit for Virtualization (Forklift) para flotas desde vSphere, oVirt u OpenStack. |

## ¿Contenedores o VMs?

| Elige un contenedor cuando | Elige una VM cuando |
|---|---|
| La app ya está empaquetada como imagen | La app necesita su propio kernel, módulos del kernel o un sistema operativo distinto |
| Quieres arranque rápido y alta densidad | Es un appliance de un fabricante o un sistema legacy que no puedes reconstruir |
| El escalamiento es horizontal | El software se licencia o certifica por VM |

No tienes que elegir para todo el data center: en una sola plataforma, cada carga de trabajo se mueve cuando está lista.

## A dónde ir después

- **Guía de usuario de KubeVirt:** https://kubevirt.io/user-guide/
- **Instance types y preferences:** tamaños de VM como los flavors de la nube (`kubectl get virtualmachineclusterinstancetypes`).
- **Forklift / Migration Toolkit for Virtualization:** migración masiva desde vSphere, oVirt y OpenStack.
- **GitOps para VMs:** las VMs son YAML, así que Argo CD o Flux pueden administrarlas.
- **Este workshop:** los extras a tu propio ritmo en el menú profundizan en contenedores, redes y almacenamiento de Kubernetes.

## Preguntas

Tu cluster sigue disponible hasta que el instructor lo reinicie. Todo lo de aquí se puede repetir en cualquier cluster con KubeVirt y CDI.

Gracias por asistir a Texas Linux Fest 2026.
