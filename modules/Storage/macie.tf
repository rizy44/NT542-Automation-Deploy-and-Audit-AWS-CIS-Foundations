resource "aws_macie2_account" "this" {
  finding_publishing_frequency = var.macie_finding_frequency
  status                       = "ENABLED"
}


resource "aws_macie2_custom_data_identifier" "pii" {
  name        = "storage-pii-identifier-${var.environment}"
  description = "Detects common PII patterns such as SSN (###-##-####)"
  regex       = var.macie_pii_regex
  keywords    = ["ssn", "social security", "taxpayer id"]

  maximum_match_distance = 50

  tags = merge(local.common_tags, {
    Name = "storage-pii-identifier-${var.environment}"
  })

  depends_on = [aws_macie2_account.this]
}


resource "aws_macie2_classification_job" "data_bucket_scan" {
  name        = "storage-data-bucket-scan-${var.environment}"
  description = "Daily scan of the data S3 bucket for sensitive data (CIS)"
  job_type    = "SCHEDULED"
  job_status  = "RUNNING"

  custom_data_identifier_ids = [aws_macie2_custom_data_identifier.pii.id]

  s3_job_definition {
    bucket_definitions {
      account_id = data.aws_caller_identity.current.account_id
      buckets    = [aws_s3_bucket.data.id]
    }
  }

  schedule_frequency {
    daily_schedule = true
  }

  tags = merge(local.common_tags, {
    Name = "storage-data-bucket-scan-${var.environment}"
  })

  depends_on = [
    aws_macie2_account.this,
    aws_macie2_custom_data_identifier.pii,
    aws_s3_bucket_policy.macie_findings
  ]
}


resource "null_resource" "macie_discovery_export_config" {
  triggers = {
    bucket_name = aws_s3_bucket.macie_findings.id
    kms_key_arn = aws_kms_key.s3.arn
  }

  provisioner "local-exec" {
    interpreter = ["bash", "-c"]
    # Đã gộp thành 1 dòng duy nhất để tránh lỗi bash line continuation
    command = "aws macie2 put-classification-export-configuration --region ${var.aws_region} --configuration '{\"s3Destination\":{\"bucketName\":\"${aws_s3_bucket.macie_findings.id}\",\"kmsKeyArn\":\"${aws_kms_key.s3.arn}\"}}'"
  }

  depends_on = [
    aws_macie2_account.this,
    aws_s3_bucket_policy.macie_findings,
    aws_kms_key.s3
  ]
}