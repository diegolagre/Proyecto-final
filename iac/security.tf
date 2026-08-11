resource "aws_kms_key" "data" {
  count = var.create_security_baseline ? 1 : 0

  description             = "Cifrado de datos para ${local.name_prefix}"
  enable_key_rotation     = true
  deletion_window_in_days = 30

  tags = { Name = "${local.name_prefix}-data" }

  lifecycle {
    precondition {
      condition     = !var.use_localstack
      error_message = "create_security_baseline sólo puede habilitarse contra AWS real."
    }
  }
}

resource "aws_kms_alias" "data" {
  count = var.create_security_baseline ? 1 : 0

  name          = "alias/${local.name_prefix}-data"
  target_key_id = aws_kms_key.data[0].key_id
}

data "aws_iam_policy_document" "require_tls" {
  for_each = var.use_localstack ? {} : {
    landing = aws_s3_bucket.landing
    curated = aws_s3_bucket.curated
  }

  statement {
    sid    = "DenyInsecureTransport"
    effect = "Deny"
    actions = [
      "s3:*"
    ]
    resources = [
      each.value.arn,
      "${each.value.arn}/*"
    ]

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = ["false"]
    }
  }
}

resource "aws_s3_bucket_policy" "require_tls" {
  for_each = data.aws_iam_policy_document.require_tls

  bucket = each.key == "landing" ? aws_s3_bucket.landing.id : aws_s3_bucket.curated.id
  policy = each.value.json
}
