# Lab 0 — TexasLinuxFest 2026: bienvenida y verificación del entorno

**Tiempo sugerido:** 10 minutos  
**Condición de éxito:** puedes llegar al API del cluster, listar los nodos, confirmar que KubeVirt está saludable, y conoces tu namespace asignado y la ruta de 2 horas.

## Por qué existe este lab

Este workshop comprime la ruta completa de Unified Workload Migration en una sola sesión de 2 horas. El Lab 0 garantiza que nadie gaste esas dos horas peleando con problemas de acceso: verificamos el entorno una vez, entre todos, antes de que empiece el contenido.

## La ruta (2 horas)

| Hora | Bloque | Minutos |
|---|---|---:|
| 0:00 | Lab 0 — TexasLinuxFest 2026 (este lab) | 10 |
| 0:10 | 1. Fundamentos de contenedores | 10 |
| 0:20 | 2. Fundamentos de Kubernetes | 15 |
| 0:35 | 3. Redes de Kubernetes | 10 |
| 0:45 | 4. Almacenamiento de Kubernetes | 10 |
| 0:55 | 5. Conceptos de KubeVirt | 15 |
| 1:10 | 6. Desplegar y operar VMs | 15 |
| 1:25 | Lab 4 — VM funcional | 25 |
| 1:50 | 7. Operaciones y siguientes pasos | 10 |

## Pasos

1. **Confirma tus herramientas.** Necesitas `kubectl` (u `oc` en OpenShift) y el plugin `virtctl`:

   ```bash
   kubectl version
   virtctl version
   ```

2. **Confirma el acceso al cluster.** Inicia sesión si tu instructor proporciona URL y token, y lista los nodos:

   ```bash
   kubectl get nodes -o wide
   ```

3. **Confirma que KubeVirt está saludable:**

   ```bash
   kubectl get kubevirt -A
   kubectl get pods -n kubevirt
   ```

   En OpenShift, revisa el operador HyperConverged: `kubectl get hco -n openshift-cnv`.

4. **Entra a tu namespace.** Tu instructor asigna un namespace por participante o equipo:

   ```bash
   kubectl config set-context --current --namespace=kubevirt-workshop
   kubectl get all
   ```

5. **Conoce la meta.** En el Lab 4 importarás una imagen cloud con CDI, arrancarás una VM Linux con disco persistente, iniciarás un servidor HTTP dentro del guest y lo validarás mediante un Service de Kubernetes con `curl`. Cada módulo anterior enseña exactamente una pieza de ese ejercicio.

## Si algo falla

Levanta la mano ahora — no esperes. Los problemas de acceso, capacidad y descarga de imágenes son del entorno, no del participante, y toda la sesión se apoya en esta verificación.
