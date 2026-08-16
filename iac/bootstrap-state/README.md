# Bootstrap del estado remoto

Esta configuración crea una única vez el backend productivo de Terraform:

- bucket S3 privado, cifrado y versionado;
- tabla DynamoDB on-demand con cifrado y recuperación point-in-time;
- protección `prevent_destroy` en ambos recursos.

No utiliza LocalStack ni contiene credenciales. AWS debe autenticarse mediante
un perfil, variables de entorno temporales o un rol federado.

## 1. Crear la capa de estado

```bash
cd iac/bootstrap-state
terraform init
terraform plan -out=bootstrap.tfplan
terraform apply bootstrap.tfplan
terraform output
```

El bucket incorpora el ID de la cuenta AWS para obtener un nombre globalmente
único. El estado local de este bootstrap no se versiona y debe custodiarse hasta
completar la migración del stack principal.

## 2. Inicializar el stack productivo

Reemplazar `<bucket>` y `<tabla>` con los outputs anteriores:

```bash
cd ..
terraform init -reconfigure \
  -backend-config="bucket=<bucket>" \
  -backend-config="key=prod/terraform.tfstate" \
  -backend-config="region=us-east-1" \
  -backend-config="dynamodb_table=<tabla>" \
  -backend-config="encrypt=true"
```

Si ya existe estado local, utilizar `-migrate-state` en lugar de
`-reconfigure` y revisar el mensaje de confirmación antes de aceptar.

## Desarrollo local

La demostración con LocalStack no utiliza el backend productivo:

```bash
cd iac
terraform init -backend=false
```

S3 y DynamoDB pertenecen al plano de administración de Terraform y no modifican
la lista de diez servicios funcionales evaluados para la solución analítica.
