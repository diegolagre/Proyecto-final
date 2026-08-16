resource "aws_route_table" "private" {
  vpc_id = aws_vpc.analytics.id

  tags = { Name = "${local.name_prefix}-private" }
}

resource "aws_route_table_association" "private" {
  count = length(aws_subnet.private)

  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private.id
}

resource "aws_security_group" "vpc_endpoints" {
  count = var.create_private_endpoints ? 1 : 0

  name        = "${local.name_prefix}-vpc-endpoints"
  description = "HTTPS desde ETL hacia endpoints privados de servicios AWS"
  vpc_id      = aws_vpc.analytics.id

  ingress {
    description     = "HTTPS desde el worker ETL"
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    security_groups = [aws_security_group.etl.id]
  }

  egress = []
}

resource "aws_vpc_endpoint" "s3" {
  count = var.create_private_endpoints ? 1 : 0

  vpc_id            = aws_vpc.analytics.id
  service_name      = "com.amazonaws.${var.region}.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = [aws_route_table.private.id]

  tags = { Name = "${local.name_prefix}-s3" }
}

resource "aws_vpc_endpoint" "interface" {
  for_each = var.create_private_endpoints ? toset([
    "secretsmanager",
    "logs",
    "monitoring"
  ]) : toset([])

  vpc_id              = aws_vpc.analytics.id
  service_name        = "com.amazonaws.${var.region}.${each.value}"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = aws_subnet.private[*].id
  security_group_ids  = [aws_security_group.vpc_endpoints[0].id]
  private_dns_enabled = true

  tags = { Name = "${local.name_prefix}-${each.value}" }
}

resource "aws_vpc_security_group_egress_rule" "etl_to_database" {
  security_group_id            = aws_security_group.etl.id
  referenced_security_group_id = aws_security_group.database.id
  description                  = "PostgreSQL hacia RDS"
  ip_protocol                  = "tcp"
  from_port                    = 5432
  to_port                      = 5432
}

resource "aws_vpc_security_group_egress_rule" "etl_to_interface_endpoints" {
  count = var.create_private_endpoints ? 1 : 0

  security_group_id            = aws_security_group.etl.id
  referenced_security_group_id = aws_security_group.vpc_endpoints[0].id
  description                  = "HTTPS hacia Secrets Manager y CloudWatch"
  ip_protocol                  = "tcp"
  from_port                    = 443
  to_port                      = 443
}

resource "aws_vpc_security_group_egress_rule" "etl_to_s3" {
  count = var.create_private_endpoints ? 1 : 0

  security_group_id = aws_security_group.etl.id
  prefix_list_id    = aws_vpc_endpoint.s3[0].prefix_list_id
  description       = "HTTPS hacia S3 mediante Gateway Endpoint"
  ip_protocol       = "tcp"
  from_port         = 443
  to_port           = 443
}
