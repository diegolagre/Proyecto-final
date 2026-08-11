# Gestión del cambio, comunicación y transferencia operativa

## Objetivo

Asegurar que la migración de la plataforma analítica no sea solamente técnica:
usuarios, soporte y operaciones deben conocer el cambio, validar los reportes y
quedar preparados para operar la solución después del hypercare.

## Grupos involucrados

| Grupo | Impacto | Responsabilidad |
|---|---|---|
| Usuarios de negocio CO-PA | Cambia la fuente técnica de los reportes | Validar cifras, filtros y tiempos de respuesta |
| Equipo SAP funcional | Mantiene definiciones y conciliaciones | Aprobar reglas de negocio y diferencias |
| SAP Basis / SLT | Opera la extracción y la delta queue | Monitorear SLT, ODP/OData y resolver bloqueos |
| Equipo cloud y datos | Opera ingesta, ETL, S3 y RDS | Alarmas, capacidad, seguridad y recuperación |
| Soporte BI | Administra gateway y datasets | Refrescos, accesos y atención de incidentes |
| Seguridad | Revisa accesos, cifrado y trazabilidad | Aprobar controles y excepciones |

## Plan de comunicación

| Momento | Audiencia | Mensaje y canal | Evidencia |
|---|---|---|---|
| Semana 1 | Stakeholders | Alcance, beneficios, exclusiones y responsables; reunión inicial | Acta y RACI aprobados |
| Semana 4 | Usuarios clave | Demostración del flujo y criterios de aceptación | Lista de observaciones |
| Semana 7 | Negocio, soporte y seguridad | Resultado de pruebas, fecha tentativa y reversa | Go/No-Go preliminar |
| 48 horas antes | Todos los consumidores | Ventana, impacto esperado y contacto de soporte | Comunicación enviada |
| Durante el corte | Equipo de migración | Estado cada hora y registro de decisiones | Bitácora de corte |
| Después del corte | Usuarios y operaciones | Resultado, incidencias conocidas y soporte | Confirmación de servicio |

## Capacitación

- Usuarios: acceso, actualización de datasets, interpretación de la nueva fecha
  de última carga y canal de incidentes.
- Soporte BI: operación del clúster de Power BI Gateway, credenciales de sólo
  lectura y diagnóstico de refrescos.
- Operaciones: tableros de CloudWatch, delta detenida, capacidad de RDS,
  restauración y escalamiento.
- SAP Basis: control de SLT, cola delta, publicación ODP/OData y conciliación.

Cada sesión tendrá asistencia, material compartido y una comprobación práctica.
Se considera aprobada cuando al menos un titular y un suplente por función
pueden ejecutar el procedimiento correspondiente sin ayuda del proyecto.

## Adopción y aceptación

Durante las pruebas de usuario se comparan filas, importes y reportes críticos
contra la plataforma anterior. La diferencia máxima aceptada es 0,1 % y debe
estar explicada. La plataforma anterior permanece disponible en modo consulta
durante el hypercare para reducir el riesgo de adopción.

Indicadores de adopción:

- 100 % de reportes críticos validados antes del Go-Live.
- 100 % de roles operativos con titular y suplente capacitados.
- Cero incidentes críticos abiertos al finalizar cinco días hábiles de hypercare.
- Al menos 90 % de refrescos BI completados dentro de la ventana acordada.

## Transferencia a operaciones

La transferencia requiere runbooks de alarmas, matriz de escalamiento, inventario
de accesos, responsables de costos, evidencia de backup/restauración y tablero de
salud. El equipo de proyecto acompaña durante el hypercare y entrega formalmente
la operación cuando se cumplen los indicadores anteriores.
