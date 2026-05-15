# ---------------------------------------------------------------------------
# Networking
# ---------------------------------------------------------------------------

output "rds_security_group_id" {
  description = "Security group ID attached to RDS"
  value       = aws_security_group.rds.id
}

output "efs_security_group_id" {
  description = "Security group ID attached to EFS mount targets"
  value       = aws_security_group.efs.id
}

# ---------------------------------------------------------------------------
# KMS
# ---------------------------------------------------------------------------

output "kms_s3_key_arn" {
  description = "ARN of the KMS key used for S3 encryption"
  value       = aws_kms_key.s3.arn
}

output "kms_rds_key_arn" {
  description = "ARN of the KMS key used for RDS encryption"
  value       = aws_kms_key.rds.arn
}

output "kms_efs_key_arn" {
  description = "ARN of the KMS key used for EFS encryption"
  value       = aws_kms_key.efs.arn
}

# ---------------------------------------------------------------------------
# S3
# ---------------------------------------------------------------------------

output "data_bucket_name" {
  description = "Name of the S3 data bucket"
  value       = aws_s3_bucket.data.id
}

output "data_bucket_arn" {
  description = "ARN of the S3 data bucket"
  value       = aws_s3_bucket.data.arn
}

output "macie_findings_bucket_name" {
  description = "Name of the Macie findings S3 bucket"
  value       = aws_s3_bucket.macie_findings.id
}

output "macie_findings_bucket_arn" {
  description = "ARN of the Macie findings S3 bucket"
  value       = aws_s3_bucket.macie_findings.arn
}

# ---------------------------------------------------------------------------
# Macie
# ---------------------------------------------------------------------------

output "macie_classification_job_id" {
  description = "ID of the Macie daily classification job"
  value       = aws_macie2_classification_job.data_bucket_scan.id
}

output "macie_custom_identifier_id" {
  description = "ID of the Macie custom PII data identifier"
  value       = aws_macie2_custom_data_identifier.pii.id
}

# ---------------------------------------------------------------------------
# RDS
# ---------------------------------------------------------------------------

output "rds_endpoint" {
  description = "Endpoint (host:port) of the RDS MySQL instance"
  value       = aws_db_instance.mysql.endpoint
}

output "rds_port" {
  description = "Port the RDS MySQL instance listens on"
  value       = aws_db_instance.mysql.port
}

output "rds_db_name" {
  description = "Name of the initial database on the RDS instance"
  value       = aws_db_instance.mysql.db_name
}

output "rds_arn" {
  description = "ARN of the RDS MySQL instance"
  value       = aws_db_instance.mysql.arn
}

# ---------------------------------------------------------------------------
# EFS
# ---------------------------------------------------------------------------

output "efs_id" {
  description = "ID of the EFS file system"
  value       = aws_efs_file_system.main.id
}

output "efs_arn" {
  description = "ARN of the EFS file system"
  value       = aws_efs_file_system.main.arn
}

output "efs_dns_name" {
  description = "DNS name of the EFS file system"
  value       = aws_efs_file_system.main.dns_name
}

output "efs_mount_target_az_a_id" {
  description = "ID of the EFS mount target in AZ A"
  value       = aws_efs_mount_target.az_a.id
}

output "efs_mount_target_az_b_id" {
  description = "ID of the EFS mount target in AZ B"
  value       = aws_efs_mount_target.az_b.id
}

output "efs_access_point_id" {
  description = "ID of the EFS access point"
  value       = aws_efs_access_point.app.id
}