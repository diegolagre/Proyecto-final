output "vpc_id" {
  value       = aws_vpc.analytics.id
  description = "VPC de la plataforma analítica."
}

output "private_subnet_ids" {
  value       = aws_subnet.private[*].id
  description = "Subredes privadas para ETL y base de datos."
}

output "landing_bucket" {
  value       = aws_s3_bucket.landing.bucket
  description = "Bucket de datos recibidos desde SAP SLT."
}

output "curated_bucket" {
  value       = aws_s3_bucket.curated.bucket
  description = "Bucket de datos validados y transformados."
}

output "etl_role_arn" {
  value       = aws_iam_role.etl.arn
  description = "Rol IAM utilizado por el proceso ETL."
}

output "etl_autoscaling_group_name" {
  value       = var.create_compute ? aws_autoscaling_group.etl[0].name : null
  description = "Auto Scaling Group de workers ETL cuando create_compute=true."
}

output "appflow_arn" {
  value       = var.create_appflow ? aws_appflow_flow.sap_copa_to_landing[0].arn : null
  description = "Flujo SAP OData a S3 cuando create_appflow=true."
}

output "rds_endpoint" {
  value       = var.create_rds ? aws_db_instance.analytics[0].address : null
  description = "Endpoint privado de RDS cuando create_rds=true."
  sensitive   = true
}
