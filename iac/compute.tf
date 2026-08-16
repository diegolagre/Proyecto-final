resource "aws_launch_template" "etl" {
  count = var.create_compute ? 1 : 0

  name_prefix   = "${local.name_prefix}-etl-"
  image_id      = var.ec2_ami_id
  instance_type = var.ec2_instance_type

  iam_instance_profile {
    name = aws_iam_instance_profile.etl.name
  }

  vpc_security_group_ids = [aws_security_group.etl.id]

  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "required"
  }

  block_device_mappings {
    device_name = "/dev/xvda"
    ebs {
      encrypted   = true
      volume_type = "gp3"
      volume_size = 30
    }
  }

  user_data = base64encode(<<-USER_DATA
    #!/usr/bin/env bash
    set -euo pipefail
    echo "Worker ETL listo. El artefacto de aplicación se despliega mediante CI/CD."
  USER_DATA
  )

  tag_specifications {
    resource_type = "instance"
    tags = {
      Name = "${local.name_prefix}-etl-worker"
      Role = "etl"
    }
  }

  lifecycle {
    create_before_destroy = true

    precondition {
      condition     = var.ec2_ami_id != "ami-00000000000000000"
      error_message = "Cuando create_compute=true se debe indicar una AMI aprobada para el worker ETL."
    }
  }
}

resource "aws_autoscaling_group" "etl" {
  count = var.create_compute ? 1 : 0

  name                = "${local.name_prefix}-etl"
  min_size            = var.environment == "prod" ? 1 : 0
  desired_capacity    = 1
  max_size            = var.environment == "prod" ? 4 : 2
  vpc_zone_identifier = aws_subnet.private[*].id
  health_check_type   = "EC2"

  launch_template {
    id      = aws_launch_template.etl[0].id
    version = "$Latest"
  }

  dynamic "tag" {
    for_each = {
      Name        = "${local.name_prefix}-etl-worker"
      Project     = var.project_name
      Environment = var.environment
    }
    content {
      key                 = tag.key
      value               = tag.value
      propagate_at_launch = true
    }
  }

  instance_refresh {
    strategy = "Rolling"
    preferences { min_healthy_percentage = 50 }
  }

  lifecycle {
    # desired_capacity sólo establece el valor inicial. Después del despliegue,
    # la política de Auto Scaling es la autoridad sobre la capacidad efectiva.
    ignore_changes = [desired_capacity]
  }
}

resource "aws_autoscaling_policy" "etl_cpu" {
  count = var.create_compute ? 1 : 0

  name                   = "${local.name_prefix}-etl-cpu"
  autoscaling_group_name = aws_autoscaling_group.etl[0].name
  policy_type            = "TargetTrackingScaling"

  target_tracking_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ASGAverageCPUUtilization"
    }
    target_value = 60
  }
}
