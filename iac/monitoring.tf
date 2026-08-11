resource "aws_cloudwatch_metric_alarm" "rds_cpu" {
  count = var.create_rds ? 1 : 0

  alarm_name          = "${local.name_prefix}-rds-high-cpu"
  alarm_description   = "RDS supera 70 % de CPU durante 15 minutos."
  namespace           = "AWS/RDS"
  metric_name         = "CPUUtilization"
  dimensions          = { DBInstanceIdentifier = aws_db_instance.analytics[0].identifier }
  comparison_operator = "GreaterThanThreshold"
  statistic           = "Average"
  period              = 300
  evaluation_periods  = 3
  threshold           = 70
  treat_missing_data  = "notBreaching"
  alarm_actions       = var.alarm_actions
}

resource "aws_cloudwatch_metric_alarm" "rds_free_storage" {
  count = var.create_rds ? 1 : 0

  alarm_name          = "${local.name_prefix}-rds-low-storage"
  alarm_description   = "RDS tiene menos de 10 % del almacenamiento inicial disponible."
  namespace           = "AWS/RDS"
  metric_name         = "FreeStorageSpace"
  dimensions          = { DBInstanceIdentifier = aws_db_instance.analytics[0].identifier }
  comparison_operator = "LessThanThreshold"
  statistic           = "Average"
  period              = 300
  evaluation_periods  = 2
  threshold           = var.database_allocated_storage * 1024 * 1024 * 1024 * 0.1
  treat_missing_data  = "missing"
  alarm_actions       = var.alarm_actions
}
