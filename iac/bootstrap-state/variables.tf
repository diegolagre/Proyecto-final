variable "project_name" {
  type        = string
  description = "Prefijo estable para los recursos del backend remoto."
  default     = "sap-analytics-migration"
}

variable "region" {
  type        = string
  description = "Región donde se almacenan el estado y el lock."
  default     = "us-east-1"
}
