variable "project_name" {
  type        = string
  description = "Slug usado para nombrar y etiquetar los recursos."
  default     = "sap-analytics-migration"
}

variable "environment" {
  type        = string
  description = "Entorno de despliegue."
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment debe ser dev, staging o prod."
  }
}

variable "region" {
  type        = string
  description = "Región AWS."
  default     = "us-east-1"
}

variable "use_localstack" {
  type        = bool
  description = "Configura los endpoints del provider contra LocalStack."
  default     = true
}

variable "localstack_endpoint" {
  type        = string
  description = "Endpoint único de LocalStack."
  default     = "http://localhost:4566"
}

variable "vpc_cidr" {
  type        = string
  description = "CIDR principal de la VPC."
  default     = "10.20.0.0/16"
}

variable "private_subnet_cidrs" {
  type        = list(string)
  description = "CIDR de las subredes privadas por zona de disponibilidad."
  default     = ["10.20.10.0/24", "10.20.20.0/24"]
}

variable "create_compute" {
  type        = bool
  description = "Crea el Auto Scaling Group de workers EC2 ETL en AWS."
  default     = false
}

variable "ec2_ami_id" {
  type        = string
  description = "AMI para el worker ETL; debe reemplazarse al desplegar en AWS real."
  default     = "ami-00000000000000000"
}

variable "create_appflow" {
  type        = bool
  description = "Crea el flujo productivo SAP OData a S3. No está disponible en la simulación local."
  default     = false
}

variable "appflow_connector_profile_name" {
  type        = string
  description = "Nombre de un Connector Profile SAPOData previamente creado con credenciales seguras."
  default     = null

  validation {
    condition     = !var.create_appflow || var.appflow_connector_profile_name != null
    error_message = "Cuando create_appflow=true se debe indicar appflow_connector_profile_name."
  }
}

variable "appflow_sap_object_path" {
  type        = string
  description = "EntitySet OData que expone la tabla CO-PA desde el proveedor ODP de SLT."
  default     = "REPLACE_WITH_COPA_ENTITY_SET"
}

variable "appflow_schedule_expression" {
  type        = string
  description = "Frecuencia de extracción incremental de AppFlow."
  default     = "rate(1 hour)"
}

variable "create_rds" {
  type        = bool
  description = "Crea RDS real. Debe permanecer false para la demostración LocalStack."
  default     = false
}

variable "database_name" {
  type        = string
  description = "Nombre de la base analítica."
  default     = "analytics"
}

variable "database_username" {
  type        = string
  description = "Usuario administrador inicial de RDS."
  default     = "analytics_admin"
}

variable "database_password" {
  type        = string
  description = "Contraseña inicial de RDS. Sólo se usa cuando create_rds=true."
  sensitive   = true
  default     = null

  validation {
    condition     = !var.create_rds || (var.database_password != null && length(var.database_password) >= 16)
    error_message = "Cuando create_rds=true, database_password debe tener al menos 16 caracteres."
  }
}
