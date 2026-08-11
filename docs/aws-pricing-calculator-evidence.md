# Evidencia de AWS Pricing Calculator

El presupuesto reproducible del repositorio no reemplaza la evidencia solicitada
por el profesor en AWS Pricing Calculator. Esta evidencia debe generarse con los
supuestos de [`cost-estimate.md`](cost-estimate.md) cerca de la fecha de entrega.

## Datos que deben cargarse

- Región: `us-east-1`.
- EC2 Linux `m6i.large`: 730 horas, más 30 GB EBS gp3.
- Dos EC2 Windows `m6i.large`: 1.460 horas totales, más 100 GB EBS gp3.
- RDS PostgreSQL `db.m6g.large` Multi-AZ: 730 horas, 100 GB gp3 y 30 GB de
  backup adicional.
- S3 Standard: 200 GB, 10.000 PUT y 100.000 GET mensuales.
- AppFlow: 730 ejecuciones y 2 GB procesados por mes.
- Site-to-Site VPN: 730 horas y 20 GB de transferencia saliente.
- CloudWatch: seis alarmas y 5 GB de logs.
- Una clave KMS, 20.000 solicitudes y tres secretos.

## Evidencia requerida antes de entregar

- [ ] Crear la estimación en <https://calculator.aws/>.
- [ ] Confirmar que el total y cada renglón son coherentes con el modelo local.
- [ ] Guardar el enlace compartido de la estimación.
- [ ] Exportar el PDF o tomar capturas donde se vean región, servicios y total.
- [ ] Agregar los archivos exportados bajo `outputs/aws-pricing-calculator/`.
- [ ] Registrar aquí la fecha, el enlace y cualquier diferencia de precio.

| Campo | Valor |
|---|---|
| Fecha de verificación | Pendiente |
| Enlace compartido | Pendiente |
| Total mensual oficial | Pendiente |
| Diferencia frente a USD 662,22 | Pendiente |

No se incluye un enlace ficticio: esta sección permanece pendiente hasta que la
estimación sea creada realmente en AWS Pricing Calculator.
