# Evidencia de AWS Pricing Calculator

La estimación fue creada en AWS Pricing Calculator y exportada como PDF. El
presupuesto reproducible del repositorio fue reconciliado contra esa evidencia.

## Datos que deben cargarse

- Región: `us-east-1`.
- EC2 Linux `m6i.large`: 730 horas, más 30 GB EBS gp3.
- Dos EC2 Windows `m6i.large`: 1.460 horas totales, más 100 GB EBS gp3.
- RDS PostgreSQL `db.m6g.large` Multi-AZ: 730 horas, 100 GB gp3 y 30 GB de
  backup adicional.
- S3 Standard: 200 GB, 10.000 PUT y 100.000 GET mensuales.
- AppFlow: 730 ejecuciones y 2 GB procesados por mes.
- Site-to-Site VPN: 730 horas, calculadas por separado porque el servicio no está
  disponible en el catálogo del Calculator público.
- CloudWatch: seis alarmas y 5 GB de logs.
- Una clave KMS, 20.000 solicitudes y tres secretos.

## Evidencia requerida antes de entregar

- [x] Crear la estimación en <https://calculator.aws/>.
- [x] Confirmar que el total y cada renglón son coherentes con el modelo local.
- [x] Guardar el enlace compartido de la estimación.
- [x] Exportar el PDF con región, servicios y total.
- [x] Agregar el archivo bajo `outputs/aws-pricing-calculator/`.
- [x] Registrar la fecha, el enlace y las diferencias de precio.

| Campo | Valor |
|---|---|
| Fecha de verificación | 11 de agosto de 2026 |
| Enlace compartido | <https://calculator.aws/#/estimate?id=0ab6fdd1ac2c32ff107e872747339ad9ffbed689> |
| Total mensual AWS Pricing Calculator | USD 700,04 |
| VPN complementaria | USD 36,50 |
| **Total mensual completo** | **USD 736,54** |
| Total anual recurrente | USD 8.838,48 |
| Upfront informado por Calculator | USD 0,06 |
| Total de 12 meses incluyendo upfront | USD 8.838,54 |
| Diferencia frente al modelo anterior | USD 74,32 mensuales (+11,22 %) |

La exportación oficial contiene EC2 ETL, dos nodos EC2 Windows para Power BI
Gateway, RDS PostgreSQL Multi-AZ, S3, AppFlow, Secrets Manager, KMS y CloudWatch.
AppFlow utiliza 730 ejecuciones y 0,00274 GB por ejecución, aproximadamente 2 GB
mensuales. La VPN se agrega con la tarifa oficial de USD 0,05 por conexión-hora:
730 horas × USD 0,05 = USD 36,50 mensuales.

La diferencia respecto del modelo anterior proviene principalmente de los
precios efectivos informados por Calculator para EC2 Linux y RDS. Los valores
oficiales se conservan aunque difieran de los precios unitarios consultados
previamente.
