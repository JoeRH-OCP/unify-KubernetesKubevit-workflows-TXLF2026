# Guía del instructor: sesión de 90 minutos

Esta guía cubre cómo preparar un clúster por participante (o por pareja) con la automatización de `ansible/`, cómo conducir los 90 minutos y cómo reiniciar el entorno entre sesiones. La referencia completa de la automatización está en `ansible/README.md`.

## Cronograma

| Cuándo | Qué | Tiempo |
|---|---|---|
| Una semana antes | Solicita los clústeres, llena `clusters.vault.yml` y ejecuta preflight en todos | 1 h |
| El día anterior | Ejecuta `site.yml` en todos los clústeres, revisa el resumen e imprime las tarjetas para participantes | 1 a 2 h (desatendido) |
| Una hora antes | Ejecuta `reset.yml` + `demo.yml` y luego `verify.yml`; abre tus propias pestañas de demo | 20 min |
| Entre sesiones | `reset.yml` + `demo.yml` en cada clúster | 15 min |
| Después del evento | `teardown.yml` o devuelve los clústeres | 30 min |

## 1. Preparar los clústeres

Cada orden de Red Hat Demo Platform entrega una URL de consola, el usuario `admin` y una contraseña aleatoria. Colócalos en el archivo vault:

```bash
cd ansible
cp clusters.example.yml clusters.vault.yml
ansible-vault encrypt clusters.vault.yml
ansible-vault edit clusters.vault.yml
```

Usa una entrada por clúster, con un nombre corto que coincida con la tarjeta del participante (por ejemplo, `p01` a `p20`). Después ejecuta, desde `ansible/`:

```bash
scripts/run-clusters.sh preflight.yml
```

El resumen muestra bloqueos y advertencias por clúster. Cada reporte está en `clusters/<name>/reports/preflight.md`. En clústeres de RHDP espera estas advertencias: OpenShift Virtualization y MTV instalados, administración por Argo CD y ninguna instancia de NMState. El siguiente paso se encarga de ellas.

```bash
scripts/run-clusters.sh site.yml --skip-login -- -e confirm_cnv_removal=true -e confirm_mtv_removal=true
```

Esto elimina OpenShift Virtualization y MTV, e instala KubeVirt y CDI upstream, kubevirt-manager, la imagen de marca de TXLF y las VMs de demo. Se ejecuta en lotes de 10 clústeres; calcula unos 45 minutos por lote. Vuelve a ejecutar solo los clústeres que fallaron con el comando que imprime el resumen.

Para conservar OpenShift Virtualization en algunos clústeres, define `vars: {virt_mode: cnv}` para ellos en `clusters.vault.yml`. Los módulos para participantes funcionan igual; solo cambia la versión de KubeVirt que se muestra.

## 2. Tarjeta para cada participante

Imprime una tarjeta por clúster:

| Campo | De dónde sale |
|---|---|
| URL de consola | `console_url` en `clusters.vault.yml` |
| Usuario / contraseña | `admin` / la contraseña del clúster (también válida para kubevirt-manager) |
| Página de inicio | `https://vm-web.apps.<cluster domain>` |
| kubevirt-manager | `https://kubevirt-manager.apps.<cluster domain>` |
| Sitio del workshop | la URL de GitHub Pages de este repositorio |

`clusters/<name>/logs/verify-*.log` lista las dos URLs de cada clúster.

## 3. Antes de cada sesión

```bash
scripts/run-clusters.sh reset.yml --skip-login
scripts/run-clusters.sh demo.yml --skip-login
scripts/run-clusters.sh verify.yml --skip-login
```

`--skip-login` reutiliza los tokens del último inicio de sesión; duran unas 24 horas. Quítalo para iniciar sesión de nuevo. Todos los clústeres deben mostrar 5 VMs en `Running`.

Tu propia laptop, para el proyector:
- Consola con sesión iniciada y el banner visible.
- La página de inicio de `vm-web`, mostrando un nodo.
- kubevirt-manager con sesión iniciada.
- Una terminal con fuente grande, `KUBECONFIG` apuntando a tu clúster de demo y `virtctl version` coincidiendo con v1.9.1.

## 4. Conducir los 90 minutos

| Reloj | Módulo | Qué haces | Checkpoint antes de avanzar |
|---|---|---|---|
| 0:00 | 1. Accede a tu cluster | Muestra la tarjeta, la terminal web y la descarga de `virtctl` | Todos ven 5 VMs en `Running` |
| 0:05 | 2. Una VM es un Pod | Explica VM / VMI / virt-launcher; escribe `kubectl apply` en vivo | `vm-live` en Running y SSH funciona |
| 0:20 | 3. Los discos son PVCs | Muestra `golden-image`, Block/RWX y el clon desde snapshot | DataVolume de `vm-clone-live` en `Succeeded` |
| 0:35 | 4. Migración unificada de cargas de trabajo | Proyecta la página de inicio durante `virtctl migrate`; después haz snapshot/restore en `vm-web` mientras ellos lo hacen en `vm-clone-live` | El nodo cambió; `/srv/data.txt` restaurado |
| 1:05 | 5. Exponer y observar | Selector del Service, `virtctl expose`, Observe > Metrics, gráficas de kubevirt-manager | Una consulta PromQL devuelve datos |
| 1:20 | 6. Cierre y siguientes pasos | Tabla de repaso, contenedores vs VMs, siguientes pasos, preguntas | |

Si el grupo va atrasado, recorta la Parte B del Módulo 4 (cordon) y el `virtctl expose` del Módulo 5. Nunca recortes la live migration: es el mensaje principal de la sesión.

## 5. Plan B

| Problema | Solución rápida |
|---|---|
| El clúster de un participante está roto | Forma pareja con alguien cercano; corrígelo después con `run-clusters.sh site.yml --only <name>` |
| La terminal web no inicia | Usa la ruta desde laptop (`oc login` + descarga de `virtctl`) o formen parejas |
| La descarga de `virtctl` está bloqueada | Usa la UI de kubevirt-manager para consola, start, stop y migrate |
| Migración atorada en `Scheduling` | `kubectl describe vmi vm-web`: normalmente es CPU o memoria; migra un clon en su lugar o muéstralo en tu clúster |
| Límite de descargas de Docker Hub (imagen de kubevirt-manager) | Define `kubevirt_manager_image_registry` con un mirror antes del evento (consulta `ansible/README.md`) |
| El restore nunca termina | La VM debe estar detenida: `virtctl stop` y luego `kubectl wait vmi/<name> --for=delete` |

## 6. Después del evento

```bash
scripts/run-clusters.sh teardown.yml --skip-login -- -e confirm_teardown=true
```

O simplemente devuelve las órdenes de RHDP. `teardown.yml` no reinstala OpenShift Virtualization; el auto-sync de Argo CD quedó desactivado y su configuración original está en `clusters/<name>/reports/argocd-original.yaml`.
