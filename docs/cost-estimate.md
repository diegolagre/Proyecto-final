# Estimación de costos AWS

Estimación orientativa para el escenario productivo base en `us-east-1`, con
precios On-Demand en USD consultados el 10 de agosto de 2026. No constituye una
cotización: impuestos, soporte empresarial, variaciones de consumo y cambios de
precio deben verificarse en AWS Pricing Calculator antes de aprobar el proyecto.

## Resumen mensual

| Categoría | Costo mensual |
|---|---:|
| BI connectivity | USD 282,48 |
| Database | USD 257,99 |
| Compute | USD 72,48 |
| Network | USD 38,30 |
| Monitoring | USD 3,25 |
| Storage | USD 4,69 |
| Security | USD 2,26 |
| Ingestion | USD 0,77 |
| **Total mensual estimado** | **USD 662,22** |
| **Total anual sin descuentos** | **USD 7.946,64** |

El 81,6 % del total corresponde al clúster de Power BI Gateway y a RDS
Multi-AZ. Separarlos permite discutir disponibilidad y ubicación del gateway
sin distorsionar el costo del data lake o de AppFlow.

## Supuestos incluidos

- 730 horas por mes.
- Un worker ETL Linux `m6i.large` funcionando permanentemente.
- Dos instancias Windows `m6i.large` para Power BI Gateway en alta disponibilidad.
- RDS PostgreSQL `db.m6g.large` Multi-AZ con 100 GB gp3.
- 30 GB adicionales de backups RDS por encima de la franquicia aplicable.
- 200 GB S3 Standard, incluyendo Landing, Curated, versiones y temporales.
- AppFlow ejecutado cada hora y 2 GB mensuales de deltas.
- Una conexión Site-to-Site VPN y 20 GB de transferencia saliente.
- Una clave KMS, tres secretos, seis alarmas y 5 GB de logs.

El archivo [`costs/aws-us-east-1.json`](../costs/aws-us-east-1.json) contiene
cada cantidad y precio unitario. El total puede recalcularse con:

```bash
python3 scripts/calculate_monthly_cost.py
```

## Detalle por componente

| Componente | Cálculo | Mensual |
|---|---:|---:|
| EC2 ETL | 730 h × USD 0,096 | USD 70,08 |
| EBS ETL | 30 GB × USD 0,08 | USD 2,40 |
| 2 EC2 Windows para gateway | 1.460 h × USD 0,188 | USD 274,48 |
| EBS gateways | 100 GB × USD 0,08 | USD 8,00 |
| RDS PostgreSQL Multi-AZ | 730 h × USD 0,318 | USD 232,14 |
| RDS gp3 Multi-AZ | 100 GB × USD 0,23 | USD 23,00 |
| Backup RDS adicional | 30 GB × USD 0,095 | USD 2,85 |
| S3 y solicitudes | almacenamiento + PUT/GET | USD 4,69 |
| AppFlow | 730 ejecuciones + 2 GB | USD 0,77 |
| VPN | 730 h × USD 0,05 | USD 36,50 |
| Transferencia saliente | 20 GB × USD 0,09 | USD 1,80 |
| KMS y Secrets Manager | clave, solicitudes y 3 secretos | USD 2,26 |
| CloudWatch | 6 alarmas + 5 GB de logs | USD 3,25 |

## Costo único de la carga inicial

| Concepto | Cálculo | Costo único |
|---|---:|---:|
| AppFlow, carga inicial estimada | 45 GB × USD 0,02 | USD 0,90 |
| Segundo worker ETL durante 24 horas | 24 h × USD 0,096 | USD 2,30 |
| **Total técnico incremental** | | **USD 3,20** |

Este valor no incluye horas de consultoría, tareas SAP Basis, desarrollo,
pruebas de usuario ni gestión del cambio. Tampoco incluye Direct Connect, porque
la primera fase utiliza VPN.

## Escenarios para decisión

| Escenario | Cambio | Estimación mensual |
|---|---|---:|
| Productivo base | Arquitectura completa y gateways en AWS | USD 662,22 |
| Gateway corporativo existente | Los dos nodos se operan on-premise | USD 379,74 |
| ETL programado | Worker activo unas 4 horas diarias en vez de 24/7 | aproximadamente USD 604 |
| Desarrollo | Single-AZ, tamaños menores y recursos apagables | debe calcularse por horas de uso |

La alternativa de gateway corporativo sólo es válida si la organización ya
dispone de servidores Windows, capacidad y operación de alta disponibilidad; no
es costo cero para el negocio, sino costo fuera de AWS.

## Oportunidades de optimización

1. Medir la duración real del ETL y reducir `desired_capacity` a cero entre
   ejecuciones si el proceso puede iniciarse por evento o agenda.
2. Evaluar una Reserved Instance de RDS después de estabilizar el tamaño; no se
   presupuestan descuentos antes de medir la carga.
3. Pasar Landing y versiones antiguas a clases S3 de archivo mediante lifecycle.
4. Ubicar Power BI Gateway en infraestructura corporativa existente sólo si se
   conserva la redundancia y capacidad necesarias.
5. Crear AWS Budgets con alertas al 80 % y 100 % del presupuesto mensual.
6. Revisar transferencia saliente y retención de logs con datos de los primeros
   tres meses.

## Elementos no incluidos

- IVA, impuestos y AWS Support.
- Direct Connect, puerto del proveedor y cross-connect.
- Licencias de Power BI y SAP.
- NAT Gateway, porque el diseño deberá priorizar endpoints privados.
- Ambientes productivos adicionales o recuperación en otra región.
- Mano de obra y costos internos de operación.

## Referencias de precios

- [AWS Pricing Calculator](https://calculator.aws/)
- [Precios On-Demand de Amazon EC2](https://aws.amazon.com/ec2/pricing/on-demand/)
- [Precios de Amazon RDS for PostgreSQL](https://aws.amazon.com/rds/postgresql/pricing/)
- [Precios de Amazon S3](https://aws.amazon.com/s3/pricing/)
- [Precios de Amazon AppFlow](https://aws.amazon.com/appflow/pricing/)
- [Precios de AWS Site-to-Site VPN](https://aws.amazon.com/vpn/pricing/)
- [Precios de AWS KMS](https://aws.amazon.com/kms/pricing/)
- [Precios de AWS Secrets Manager](https://aws.amazon.com/secrets-manager/pricing/)
- [Precios de Amazon CloudWatch](https://aws.amazon.com/cloudwatch/pricing/)

La tarifa de RDS utilizada se verificó además contra el catálogo público de AWS:
USD 0,318 por hora para `db.m6g.large` PostgreSQL Multi-AZ y USD 0,23 por GB-mes
de almacenamiento gp3 Multi-AZ en `us-east-1`.
