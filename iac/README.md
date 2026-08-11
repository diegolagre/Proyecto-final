# Infraestructura Terraform

Este directorio define la arquitectura objetivo en AWS y conserva LocalStack
como modo seguro por defecto. Reutiliza la estructura y las convenciones de
`cloud-foundations-lab`: variables tipadas, estado no versionado, provider local
y recursos con etiquetas consistentes.

## Recursos definidos

- VPC y dos subredes privadas.
- Security groups separados para ETL y PostgreSQL.
- Buckets S3 Landing y Curated con versionado, cifrado y bloqueo público.
- Rol e instance profile IAM de mínimo privilegio.
- Launch Template y Auto Scaling Group para workers ETL.
- Flujo AppFlow opcional SAP OData → S3 Landing.
- RDS PostgreSQL opcional, privado y Multi-AZ en producción.
- KMS, Secrets Manager administrado por RDS y alarmas CloudWatch.

## Validación local

Terraform 1.5 o superior:

```bash
cd iac
terraform init -backend=false
terraform fmt -check -recursive
terraform validate
terraform plan
```

El modo predeterminado usa LocalStack y no habilita AppFlow, EC2, RDS ni KMS.
La demostración materializa los servicios locales mediante
`scripts/bootstrap_cloud.py`, porque LocalStack Community no reproduce todos los
servicios administrados de AWS.

## Plan productivo

Ejemplo deliberadamente incompleto: los valores entre ángulos deben provenir
del equipo SAP y de la cuenta AWS antes de ejecutar el plan.

```bash
terraform plan \
  -var='environment=prod' \
  -var='use_localstack=false' \
  -var='create_appflow=true' \
  -var='appflow_connector_profile_name=<perfil-sap-odata>' \
  -var='appflow_sap_object_path=<entity-set-copa>' \
  -var='create_compute=true' \
  -var='ec2_ami_id=<ami-aprobada>' \
  -var='create_rds=true' \
  -var='create_security_baseline=true'
```

Terraform falla de forma explícita si se intenta crear AppFlow sin Connector
Profile/EntitySet, EC2 con la AMI ficticia o KMS apuntando a LocalStack.

## Credenciales y estado

- El Connector Profile se crea fuera del módulo para no persistir la contraseña
  SAP dentro del estado.
- RDS genera la contraseña maestra y la administra mediante Secrets Manager.
- El backend local sólo sirve para desarrollo. Producción debe utilizar un
  backend remoto cifrado, versionado y con bloqueo de estado.
- No se deben guardar `.tfstate`, planes, `.env` ni secretos en Git.

## Archivos

| Archivo | Responsabilidad |
|---|---|
| `providers.tf` | Versión y configuración del provider AWS/LocalStack |
| `main.tf` | VPC, S3, IAM y RDS |
| `appflow.tf` | Flujo SAP OData hacia Landing |
| `compute.tf` | Launch Template y Auto Scaling |
| `security.tf` | KMS y políticas HTTPS de S3 |
| `monitoring.tf` | Alarmas de CPU y almacenamiento RDS |
| `variables.tf` | Parámetros y valores base de dimensionamiento |
| `outputs.tf` | Identificadores y endpoints sensibles |
