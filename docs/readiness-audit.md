# Auditoría previa a la entrega

Fecha de revisión: 16 de agosto de 2026. La auditoría evalúa el contenido
versionado en `main`; no certifica servicios que sólo pueden probarse dentro de
SAP o de una cuenta AWS real.

## Resultado

**Estado del repositorio: listo para revisión académica.**

| Criterio | Estado | Evidencia |
|---|---|---|
| Caso y alcance definidos | Completo | `docs/delivery-guide.md` y `docs/architecture.md` |
| Tiempo y Gantt | Completo | `docs/migration-plan.md` |
| Recursos dimensionados | Completo | `docs/sizing.md` y variables Terraform |
| Costos mensuales | Completo | `docs/cost-estimate.md` y JSON recalculable |
| AWS Pricing Calculator | Completo | PDF oficial, enlace compartido y conciliación con VPN y PrivateLink |
| Cuatro o más servicios | Completo | Cinco servicios AWS verificados en LocalStack |
| Código reproducible | Completo | Bootstrap, demo y control con un comando |
| Seguridad | Completo para diseño | IAM, red privada, KMS, secretos y alarmas |
| Egress ETL | Completo en código | Sin salida general; reglas hacia RDS y VPC endpoints cubiertas por pruebas |
| Estado Terraform | Completo en código | Backend S3 parcial y bootstrap S3+DynamoDB protegido |
| Auto Scaling | Completo en código | `desired_capacity` inicial con `ignore_changes` y prueba automática |
| Arquitectura defendible | Completo | Decisiones y alternativas registradas |
| Cultura y procesos | Completo | Comunicación, capacitación, adopción y transferencia |
| Presentación | Completo | PowerPoint de ocho diapositivas con fuentes |
| Datos confidenciales | Protegidos | Sólo se versionan registros sintéticos |

## Controles ejecutados

- Worktree limpio antes de iniciar la auditoría.
- Historial con commits incrementales y rama `main` sincronizada.
- Trece pruebas automatizadas aprobadas.
- Demo integral: 13 controles aprobados y cero advertencias.
- Terraform/OpenTofu: formato correcto; módulos y controles estáticos
  versionados. El plan productivo requiere credenciales y cuenta AWS de prueba.
- Presentación: sin overflow y sin diferencias estructurales contra el template.
- Cálculo reconciliado: USD 700,04 en Calculator y USD 780,44 con VPN y
  PrivateLink complementarios.
- Búsqueda de credenciales: no se encontraron tokens, access keys ni contraseñas
  productivas versionadas.

Los valores `test` de AWS y `local_dev_only` de PostgreSQL son credenciales
ficticias exclusivas de LocalStack/Docker. No deben reutilizarse fuera de la demo.

## Protecciones agregadas por la auditoría

Terraform rechaza un plan productivo si:

- AppFlow no recibe un Connector Profile;
- el `EntitySet` conserva el placeholder de CO-PA;
- EC2 conserva la AMI ficticia;
- se intenta habilitar la línea base KMS contra LocalStack;
- se intentan crear endpoints privados contra LocalStack.

Además, el SG ETL carece de egress general, el ASG ignora cambios posteriores de
`desired_capacity` y el backend productivo se declara fuera del estado local.

Estas condiciones evitan que una configuración incompleta parezca un despliegue
productivo válido.

## Pendientes del alumno

1. Confirmar si la región definitiva seguirá siendo `us-east-1`.
2. Practicar la defensa con `./scripts/presentation_demo.sh`.

## Dependencias externas antes de un piloto real

1. Confirmar en SAP SLT el acceso a `CE1xxxx` y la delta queue.
2. Publicar y validar el `EntitySet` mediante SAP Gateway OData.
3. Crear el Connector Profile de AppFlow con credenciales seguras.
4. Aprobar AMI, certificados, rutas, firewall y cuenta AWS.
5. Crear el backend remoto y ejecutar `terraform plan` en una cuenta de prueba.
6. Ejecutar la prueba sintética de 4,5 millones de filas.
7. Crear usuarios PostgreSQL separados para ETL y Power BI.
8. Configurar topics SNS, responsables y runbooks de alarmas.
9. Ensayar backup, restauración, corte y reversa.

Ninguna de estas dependencias requiere exponer o versionar información CO-PA
productiva dentro del proyecto académico.
