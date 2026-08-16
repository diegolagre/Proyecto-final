output "state_bucket" {
  description = "Bucket S3 que almacena el estado remoto."
  value       = aws_s3_bucket.terraform_state.id
}

output "lock_table" {
  description = "Tabla DynamoDB utilizada para bloquear el estado."
  value       = aws_dynamodb_table.terraform_locks.name
}

output "backend_key" {
  description = "Clave recomendada para el estado productivo."
  value       = "prod/terraform.tfstate"
}
