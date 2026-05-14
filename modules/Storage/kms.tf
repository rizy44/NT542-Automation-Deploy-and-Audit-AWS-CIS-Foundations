data "aws_iam_policy_document" "s3_kms" {
  statement {
    sid    = "AllowRootAdministration"
    effect = "Allow"
    principals {
      type        = "AWS"
      identifiers = ["arn:${data.aws_partition.current.partition}:iam::${data.aws_caller_identity.current.account_id}:root"]
    }
    actions   = ["kms:*"]
    resources = ["*"]
  }

  statement {
    sid    = "AllowS3ServiceUse"
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["s3.amazonaws.com"]
    }
    actions = [
      "kms:Decrypt",
      "kms:DescribeKey",
      "kms:GenerateDataKey*",
      "kms:ReEncrypt*"
    ]
    resources = ["*"]
  }

  statement {
    sid    = "AllowMacieServiceUse"
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["macie.amazonaws.com"]
    }
    actions = [
      "kms:Decrypt",
      "kms:DescribeKey",
      "kms:Encrypt",
      "kms:GenerateDataKey*",
      "kms:ReEncrypt*"
    ]
    resources = ["*"]
    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = [data.aws_caller_identity.current.account_id]
    }
  }
}

resource "aws_kms_key" "s3" {
  description             = "KMS key for S3 data and Macie findings bucket encryption"
  deletion_window_in_days = 10
  enable_key_rotation     = true
  policy                  = data.aws_iam_policy_document.s3_kms.json

  tags = merge(local.common_tags, {
    Name = "storage-s3-kms-${var.environment}"
  })
}

resource "aws_kms_alias" "s3" {
  name          = "alias/storage-s3-${var.environment}"
  target_key_id = aws_kms_key.s3.key_id
}


data "aws_iam_policy_document" "rds_kms" {
  statement {
    sid    = "AllowRootAdministration"
    effect = "Allow"
    principals {
      type        = "AWS"
      identifiers = ["arn:${data.aws_partition.current.partition}:iam::${data.aws_caller_identity.current.account_id}:root"]
    }
    actions   = ["kms:*"]
    resources = ["*"]
  }

  statement {
    sid    = "AllowRDSServiceUse"
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["rds.amazonaws.com"]
    }
    actions = [
      "kms:Decrypt",
      "kms:DescribeKey",
      "kms:Encrypt",
      "kms:GenerateDataKey*",
      "kms:ReEncrypt*"
    ]
    resources = ["*"]
  }
}

resource "aws_kms_key" "rds" {
  description             = "KMS key for RDS MySQL encryption at rest"
  deletion_window_in_days = 10
  enable_key_rotation     = true
  policy                  = data.aws_iam_policy_document.rds_kms.json

  tags = merge(local.common_tags, {
    Name = "storage-rds-kms-${var.environment}"
  })
}

resource "aws_kms_alias" "rds" {
  name          = "alias/storage-rds-${var.environment}"
  target_key_id = aws_kms_key.rds.key_id
}


data "aws_iam_policy_document" "efs_kms" {
  statement {
    sid    = "AllowRootAdministration"
    effect = "Allow"
    principals {
      type        = "AWS"
      identifiers = ["arn:${data.aws_partition.current.partition}:iam::${data.aws_caller_identity.current.account_id}:root"]
    }
    actions   = ["kms:*"]
    resources = ["*"]
  }

  statement {
    sid    = "AllowEFSServiceUse"
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["elasticfilesystem.amazonaws.com"]
    }
    actions = [
      "kms:Decrypt",
      "kms:DescribeKey",
      "kms:Encrypt",
      "kms:GenerateDataKey*",
      "kms:ReEncrypt*"
    ]
    resources = ["*"]
  }
}

resource "aws_kms_key" "efs" {
  description             = "KMS key for EFS filesystem encryption at rest"
  deletion_window_in_days = 10
  enable_key_rotation     = true
  policy                  = data.aws_iam_policy_document.efs_kms.json

  tags = merge(local.common_tags, {
    Name = "storage-efs-kms-${var.environment}"
  })
}

resource "aws_kms_alias" "efs" {
  name          = "alias/storage-efs-${var.environment}"
  target_key_id = aws_kms_key.efs.key_id
}