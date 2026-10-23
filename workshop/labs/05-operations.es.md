# Laboratorio 5 — Operaciones, troubleshooting y siguientes pasos

**Tiempo sugerido:** 60–90 minutos  
**Objetivo:** usar herramientas nativas de Kubernetes para inspeccionar salud de VM, asignación de recursos, eventos y fallas comunes.

## Observar VM y recursos

Usa la VM del ejercicio final si está disponible:

```bash
kubectl -n kubevirt-workshop get vm,vmi,pods,svc,pvc
kubectl -n kubevirt-workshop describe vm final-functional-vm
kubectl -n kubevirt-workshop describe vmi final-functional-vm
kubectl -n kubevirt-workshop get events --sort-by=.lastTimestamp
```

En OpenShift, revisa los dashboards de virtualización y vistas de monitoreo disponibles. En Kubernetes upstream, usa el stack de métricas y logs configurado.

Analiza la diferencia entre estado deseado de VM y estado runtime de VMI; requests, límites, scheduling y tamaño del guest; capacidad del nodo frente a recursos visibles dentro del guest; cómo relacionar VM/VMI con el launcher Pod y el nodo; y por qué `Running` no demuestra que los servicios del guest estén saludables.

## Reto de troubleshooting

El instructor cambia una condición por vez o entrega un ejemplo preparado con una falla. Identifica evidencias antes de aplicar una solución.

| Síntoma | Evidencia | Área probable |
|---|---|---|
| VM continúa en Scheduling | `describe vmi`, eventos, capacidad | Recursos, labels/taints, soporte de virtualización |
| DataVolume no avanza | Condiciones DV, logs/eventos del importer | URL, TLS, aprovisionamiento |
| PVC Pending | Eventos PVC, StorageClass | Provisioner, capacidad, modo de acceso |
| VM corre pero HTTP falla | Endpoints, labels VMI, consola/cloud-init | Selector, servicio guest, red |
| VM se reinicia repetidamente | Eventos VMI, logs launcher, arranque guest | Imagen, disco, presión del nodo |

No expongas claves privadas, secretos cloud-init ni logs sensibles en capturas o commits.

## Seguridad y ubicación

- Usa roles namespace de mínimo privilegio; reserva la administración global a instructores.
- Trata las imágenes guest como insumos de la cadena de suministro: usa fuentes confiables, verifica checksums y registra procedencia.
- No incluyas contraseñas ni claves privadas en YAML plano. Usa claves SSH públicas y controles adecuados para producción.
- Define requests de CPU/memoria razonables, aplica cuotas y monitorea contención.
- Elige contenedores para componentes que aprovechan arranque rápido y densidad de kernel compartido; elige VMs si se requiere un SO guest, compatibilidad heredada o límites específicos de aislamiento.
- Considera segmentación de red y firewall del guest además de NetworkPolicy.

## Siguientes pasos

- Live migration a escala, solo en clústeres preparados.
- Redes secundarias Multus y conectividad dedicada.
- Guests Windows y drivers VirtIO.
- GPU/passthrough de dispositivos, cuando esté soportado.
- GitOps para plantillas VM y DataVolumes.
- Herramientas de migración y planificación de cutover de aplicaciones.
