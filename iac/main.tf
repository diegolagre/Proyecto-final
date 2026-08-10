locals {
  name_prefix = "${var.project_name}-${var.environment}"
  azs         = ["${var.region}a", "${var.region}b"]
}

resource "aws_vpc" "analytics" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = { Name = "${local.name_prefix}-vpc" }
}

resource "aws_subnet" "private" {
  count = length(var.private_subnet_cidrs)

  vpc_id                  = aws_vpc.analytics.id
  cidr_block              = var.private_subnet_cidrs[count.index]
  availability_zone       = local.azs[count.index]
  map_public_ip_on_launch = false

  tags = {
    Name = "${local.name_prefix}-private-${count.index + 1}"
    Tier = "private"
  }
}

resource "aws_security_group" "etl" {
  name        = "${local.name_prefix}-etl"
  description = "Egress para el worker de integracion y ETL"
  vpc_id      = aws_vpc.analytics.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "database" {
  name        = "${local.name_prefix}-database"
  description = "PostgreSQL privado, accesible solamente desde ETL"
  vpc_id      = aws_vpc.analytics.id

  ingress {
    description     = "PostgreSQL desde ETL"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.etl.id]
  }
}

resource "aws_s3_bucket" "landing" {
  bucket        = "${local.name_prefix}-landing"
  force_destroy = var.environment != "prod"
}

resource "aws_s3_bucket" "curated" {
  bucket        = "${local.name_prefix}-curated"
  force_destroy = var.environment != "prod"
}

resource "aws_s3_bucket_public_access_block" "data" {
  for_each = {
    landing = aws_s3_bucket.landing.id
    curated = aws_s3_bucket.curated.id
  }

  bucket                  = each.value
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "data" {
  for_each = {
    landing = aws_s3_bucket.landing.id
    curated = aws_s3_bucket.curated.id
  }

  bucket = each.value

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_versioning" "data" {
  for_each = {
    landing = aws_s3_bucket.landing.id
    curated = aws_s3_bucket.curated.id
  }

  bucket = each.value
  versioning_configuration { status = "Enabled" }
}

data "aws_iam_policy_document" "ec2_trust" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "etl" {
  name               = "${local.name_prefix}-etl-role"
  assume_role_policy = data.aws_iam_policy_document.ec2_trust.json
}

data "aws_iam_policy_document" "etl_data_access" {
  statement {
    sid       = "ListDataBuckets"
    effect    = "Allow"
    actions   = ["s3:ListBucket"]
    resources = [aws_s3_bucket.landing.arn, aws_s3_bucket.curated.arn]
  }

  statement {
    sid    = "ReadLanding"
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:GetObjectVersion"
    ]
    resources = ["${aws_s3_bucket.landing.arn}/*"]
  }

  statement {
    sid       = "WriteCurated"
    effect    = "Allow"
    actions   = ["s3:PutObject"]
    resources = ["${aws_s3_bucket.curated.arn}/*"]
  }
}

resource "aws_iam_role_policy" "etl_data_access" {
  name   = "${local.name_prefix}-etl-data-access"
  role   = aws_iam_role.etl.id
  policy = data.aws_iam_policy_document.etl_data_access.json
}

resource "aws_iam_instance_profile" "etl" {
  name = "${local.name_prefix}-etl-profile"
  role = aws_iam_role.etl.name
}

resource "aws_db_subnet_group" "analytics" {
  count = var.create_rds ? 1 : 0

  name       = "${local.name_prefix}-database"
  subnet_ids = aws_subnet.private[*].id
}

resource "aws_db_instance" "analytics" {
  count = var.create_rds ? 1 : 0

  identifier                   = "${local.name_prefix}-postgres"
  engine                       = "postgres"
  engine_version               = "16"
  instance_class               = "db.t4g.medium"
  allocated_storage            = 100
  max_allocated_storage        = 200
  storage_type                 = "gp3"
  storage_encrypted            = true
  db_name                      = var.database_name
  username                     = var.database_username
  password                     = var.database_password
  db_subnet_group_name         = aws_db_subnet_group.analytics[0].name
  vpc_security_group_ids       = [aws_security_group.database.id]
  publicly_accessible          = false
  multi_az                     = var.environment == "prod"
  backup_retention_period      = var.environment == "prod" ? 14 : 7
  deletion_protection          = var.environment == "prod"
  skip_final_snapshot          = var.environment != "prod"
  performance_insights_enabled = var.environment == "prod"
}
