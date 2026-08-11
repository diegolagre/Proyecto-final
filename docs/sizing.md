# Dimensionamiento inicial y escalabilidad

Este documento transforma el volumen conocido de CO-PA en un escenario inicial
de capacidad. No reemplaza una medición productiva: salvo los 45 millones de
registros y los aproximadamente 2 GiB observados en SAP Datasphere, los valores
son supuestos de planificación que deben validarse con una extracción anónima o
con estadísticas técnicas del sistema.

## Datos de entrada y supuestos

| Parámetro | Escenario base | Escenario pico | Tratamiento |
|---|---:|---:|---|
| Registros históricos CO-PA | 45 millones | 45 millones | Dato conocido |
| Tamaño observado en Datasphere | 2 GiB | 2 GiB | Referencia comprimida; no equivale al CSV ni a PostgreSQL |
| Exportación inicial CSV | 45 GiB | 54 GiB | Estimación de 1,0 a 1,2 KiB por fila |
| Dataset inicial Parquet | 6 GiB | 9 GiB | Estimación; se valida con la prueba de volumen |
| Huella inicial en PostgreSQL | 40 GiB | 60 GiB | Incluye tablas, staging, índices y agregados |
| Crecimiento anual | 20 % | 30 % | Supuesto a confirmar con negocio |
| Delta diario | 50.000 filas | 150.000 filas | Promedio y pico de diseño |
| Frecuencia incremental | Cada hora | Cada 15 minutos | La base comienza con una hora |
| Retención Landing | 90 días en línea | Igual | Después pasa a archivo |
| Retención Curated | 12 meses en línea | Igual | Histórico total archivado por 5 años |

El tamaño de Datasphere sólo demuestra que el conjunto comprimido es manejable.
No se multiplica directamente para obtener el tamaño de CSV o de RDS, porque la
compresión columnar, los tipos de datos y los índices producen relaciones muy
diferentes.

## Capacidad propuesta

### Ingesta con AppFlow

- Carga inicial dividida por ejercicio y período fiscal para permitir reinicios
  parciales y evitar una única ejecución de gran tamaño.
- Flujo incremental cada hora utilizando el delta token del proveedor ODP/OData.
- Conciliación diaria por cantidad de filas, importes y claves de negocio.
- Los archivos se particionan por ejercicio, período y fecha de extracción.
- Objetivo de 128 a 512 MiB por archivo Parquet para reducir archivos pequeños.

AppFlow admite una carga completa inicial seguida de transferencias incrementales
para proveedores ODP. La frecuencia seleccionada está muy por debajo del máximo
de una ejecución por minuto documentado por AWS.

### Amazon S3

La capacidad inicial presupuestada es 100 GiB, con una previsión de hasta 200 GiB
durante el primer año. El margen cubre Landing, Curated, reintentos, versiones y
archivos temporales; S3 no necesita preaprovisionar ese espacio.

- Landing: conservar 90 días en la clase activa y luego archivar.
- Curated: conservar 12 meses en la clase activa y archivar el histórico.
- Versionado habilitado y reglas posteriores para expirar versiones antiguas.
- Revisar objetos menores de 128 KiB antes de aplicar transiciones de clase.

### Workers ETL en EC2

| Entorno | Tipo base | Mínimo | Deseado | Máximo |
|---|---|---:|---:|---:|
| Desarrollo | `t3.medium` | 0 | 1 | 2 |
| Producción | `m6i.large` | 1 | 1 | 4 |

Cada worker procesa particiones independientes. El Auto Scaling Group aumenta la
capacidad al superar el objetivo de 60 % de CPU; para una carga inicial se puede
elevar temporalmente la capacidad deseada a dos workers. Antes del despliegue se
debe agregar una métrica de profundidad o antigüedad de la cola, porque representa
mejor el atraso real que la CPU por sí sola.

### Amazon RDS for PostgreSQL

| Entorno | Clase | Despliegue | Almacenamiento | Backups |
|---|---|---|---:|---:|
| Desarrollo | `db.t4g.medium` | Single-AZ | 50 GiB, máximo 100 GiB | 7 días |
| Producción | `db.m6g.large` | Multi-AZ | 100 GiB gp3, máximo 200 GiB | 14 días |

El valor productivo deja margen sobre la huella inicial estimada de 40–60 GiB.
gp3 aporta una línea base de 3.000 IOPS y 125 MiB/s para PostgreSQL. El umbral
máximo de 200 GiB supera ampliamente el mínimo operativo requerido para que el
autoescalado tenga espacio de maniobra. Multi-AZ protege la disponibilidad, pero
no reemplaza los backups ni las pruebas de restauración.

### Conectividad

Para la primera carga se reserva una ventana fuera de horario y al menos 100
Mbit/s efectivos sobre la VPN. Transferir 45 GiB a ese rendimiento requiere cerca
de una hora teórica, sin contar serialización, cifrado, latencia ni procesamiento;
la prueba integral definirá la ventana real. Direct Connect se justifica si el
tráfico sostenido, la estabilidad o el tiempo de carga exceden lo aceptable para
la VPN.

## Criterios de escalamiento

| Señal | Umbral inicial | Acción |
|---|---:|---|
| Atraso de ingesta | Más de 2 ejecuciones horarias | Escalar workers y revisar AppFlow/ODP |
| CPU ETL | Más de 60 % sostenido | Auto Scaling hasta 4 workers |
| Espacio libre RDS | Menos de 10 % | Autoescalado; investigar crecimiento |
| CPU RDS | Más de 70 % durante 15 minutos | Optimizar consultas o aumentar clase |
| Conexiones RDS | Más de 80 % del límite | Pool de conexiones o aumentar clase |
| Consulta BI p95 | Más de 10 segundos | Índices, agregados, capa semántica o réplica de lectura |
| Crecimiento S3 | Más de 30 % sobre la proyección | Ajustar ciclo de vida y presupuesto |

## Prueba de volumen antes de producción

1. Generar un conjunto sintético de al menos 4,5 millones de filas (10 % del
   volumen) con el mismo ancho y tipos del esquema CO-PA aprobado.
2. Medir tamaños CSV, Parquet y PostgreSQL, duración de extracción, ETL y carga.
3. Ejecutar deltas concurrentes, reintentos e idempotencia.
4. Extrapolar sólo después de registrar CPU, memoria, I/O, red y tiempos p95.
5. Repetir con 45 millones de filas si la ventana y el presupuesto lo permiten.

Los datos siguen siendo sintéticos y no contienen compañías, clientes,
materiales, documentos ni importes productivos.

## Parámetros reflejados en Terraform

El escenario productivo base queda parametrizado con:

```hcl
ec2_instance_type            = "m6i.large"
database_instance_class      = "db.m6g.large"
database_allocated_storage   = 100
database_max_allocated_storage = 200
```

El entorno de desarrollo puede sobrescribir esos valores sin modificar el
módulo. `create_appflow`, `create_compute` y `create_rds` permanecen desactivados
por defecto para que la demostración local no genere recursos ni costos reales.

## Referencias técnicas

- [SAP OData como origen de Amazon AppFlow](https://docs.aws.amazon.com/appflow/latest/userguide/sapodata.html)
- [Almacenamiento gp3 para Amazon RDS](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Storage.html)
- [Autoescalado de almacenamiento de RDS](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_PIOPS.Autoscaling.html)
- [Retención de backups automatizados de RDS](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_WorkingWithAutomatedBackups.BackupRetention.html)
- [Transiciones de ciclo de vida de Amazon S3](https://docs.aws.amazon.com/AmazonS3/latest/userguide/lifecycle-transition-general-considerations.html)
