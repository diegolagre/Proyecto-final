# Seguridad y operación

La plataforma aplica defensa en profundidad desde SAP ECC hasta la capa de
consumo. La demostración local conserva los mismos límites lógicos, pero no
pretende reemplazar los servicios administrados de seguridad de AWS.

## Controles implementados

| Área | Control productivo | Implementación |
|---|---|---|
| Red | RDS y ETL en subredes privadas | Sin ruta a Internet; ETL sólo sale a RDS y a endpoints privados de S3, Secrets Manager y CloudWatch |
| Transporte | TLS en todos los enlaces | Política S3 deniega solicitudes sin `aws:SecureTransport`; SAP OData y Power BI usan HTTPS/TLS |
| Datos en reposo | Clave KMS administrada por el proyecto | Rotación habilitada; S3 usa SSE-KMS y RDS puede usar la misma CMK |
| Secretos | Contraseña administrada por RDS | RDS genera y guarda la credencial maestra en Secrets Manager; no se ingresa en Terraform |
| Identidad | Rol EC2 de mínimo privilegio | Lee Landing, escribe Curated y sólo usa la clave KMS de datos |
| Exposición | Bloqueo público S3 y RDS privado | Public Access Block y `publicly_accessible = false` |
| Disponibilidad | RDS Multi-AZ en producción | Backups por 14 días, protección contra borrado y snapshot final |
| Monitoreo | Alarmas CloudWatch | CPU RDS superior a 70 % y espacio libre inferior a 10 % |

## Flujo de credenciales

1. Terraform solicita a RDS que administre la contraseña maestra.
2. RDS genera la contraseña y crea el secreto en AWS Secrets Manager.
3. El ARN se publica como output sensible; el valor nunca se imprime ni se
   almacena como variable del proyecto.
4. El worker ETL debe obtener una credencial de aplicación mediante un rol IAM
   específico. En producción no debe utilizar el usuario maestro.
5. Power BI Gateway utiliza otro usuario PostgreSQL de sólo lectura.

La creación de usuarios de aplicación y BI queda como tarea de inicialización
posterior al despliegue, ya que requiere conectividad privada hacia RDS.

## Separación de accesos

| Identidad | Landing | Curated | RDS |
|---|---|---|---|
| AppFlow | Escritura | Sin acceso | Sin acceso |
| Worker ETL | Lectura | Escritura | Escritura sobre staging y modelo dimensional |
| Power BI Gateway | Sin acceso | Sin acceso | Lectura sobre vistas analíticas |
| Administrador | Acceso excepcional y auditado | Acceso excepcional y auditado | Administración mediante rol separado |

## Configuración por ambiente

La línea base KMS se mantiene desactivada en LocalStack porque el laboratorio
usa HTTP y credenciales ficticias. Para AWS real se habilita explícitamente:

```hcl
use_localstack           = false
create_security_baseline = true
create_rds               = true
create_private_endpoints = true
alarm_actions            = ["arn:aws:sns:us-east-1:123456789012:analytics-alerts"]
```

Las acciones de alarma se parametrizan para no acoplar este módulo a un canal de
notificaciones. Sin `alarm_actions`, las alarmas igualmente cambian de estado,
pero no envían avisos.

## Riesgos y tareas antes de producción

- Crear un usuario ETL y otro de sólo lectura para Power BI; no compartir el
  usuario maestro.
- Validar mediante pruebas de integración que el worker ETL accede a S3,
  Secrets Manager, CloudWatch y RDS sin una ruta por Internet.
- Integrar CloudTrail y retención centralizada de logs.
- Probar restauración de RDS y recuperación de objetos S3 versionados.
- Configurar un clúster de al menos dos gateways de Power BI.
- Definir responsables y tiempos de respuesta de las alarmas.

## Referencias técnicas

- [Administración de contraseñas de RDS con Secrets Manager](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-secrets-manager.html)
- [Cifrado predeterminado de buckets S3](https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucket-encryption.html)
- [Claves KMS administradas por el cliente para Amazon RDS](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Overview.Encryption.html)
- [Métricas de Amazon RDS en CloudWatch](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/monitoring-cloudwatch.html)
