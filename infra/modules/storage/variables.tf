variable "environment" {
  description = "Environment label (dev / staging / prod)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name for resource tagging and naming"
  type        = string
  default     = "cis-baseline"
}

variable "vpc_id" {
  description = "VPC ID from the network module"
  type        = string
}

variable "private_subnet_ids" {
  description = "Private subnet IDs from the network module"
  type        = list(string)
}

variable "vpc_cidr_block" {
  description = "CIDR block of the imported VPC, used for security group ingress rules"
  type        = string
}

# S3
variable "data_bucket_name_prefix" {
  description = "Prefix for the main S3 data bucket"
  type        = string
  default     = "storage-data"
}

variable "macie_bucket_name_prefix" {
  description = "Prefix for the Macie findings S3 bucket"
  type        = string
  default     = "storage-macie-findings"
}

# Macie
variable "macie_finding_frequency" {
  description = "Frequency for publishing Macie findings (FIFTEEN_MINUTES / ONE_HOUR / SIX_HOURS)"
  type        = string
  default     = "ONE_HOUR"
}

variable "macie_pii_regex" {
  description = "Regex pattern used by the Macie custom data identifier for PII detection (SSN format by default)"
  type        = string
  default     = "\\b\\d{3}-\\d{2}-\\d{4}\\b"
}

variable "enable_macie" {
  description = "Whether to enable Macie resources. Disable in AWS Learner Lab when macie2:EnableMacie is blocked."
  type        = bool
  default     = true
}

# RDS (MySQL)
variable "rds_engine_version" {
  description = "MySQL engine version"
  type        = string
  default     = "8.0"
}

variable "rds_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.medium"
}

variable "rds_allocated_storage" {
  description = "Allocated storage in GiB"
  type        = number
  default     = 20
}

variable "rds_db_name" {
  description = "Name of the initial database"
  type        = string
  default     = "appdb"
}

variable "rds_master_username" {
  description = "Master username for RDS"
  type        = string
  default     = "dbadmin"
}

variable "rds_master_password" {
  description = "Master password for RDS. In production prefer TF_VAR_rds_master_password env var or AWS Secrets Manager."
  type        = string
  sensitive   = true
}

variable "rds_backup_retention_days" {
  description = "Days to retain automated backups (CIS 2.3.3 requires > 0)"
  type        = number
  default     = 7
}

variable "rds_multi_az" {
  description = "Enable Multi-AZ deployment for RDS (Primary + Standby)"
  type        = bool
  default     = true
}

variable "rds_deletion_protection" {
  description = "Enable deletion protection on the RDS instance"
  type        = bool
  default     = true
}

variable "rds_skip_final_snapshot" {
  description = "Skip the final DB snapshot when deleting the instance"
  type        = bool
  default     = false
}

variable "enable_rds_monitoring" {
  description = "Whether to create the IAM role for RDS enhanced monitoring and enable enhanced monitoring."
  type        = bool
  default     = true
}

# EFS
variable "efs_performance_mode" {
  description = "EFS performance mode (generalPurpose / maxIO)"
  type        = string
  default     = "generalPurpose"
}

variable "efs_throughput_mode" {
  description = "EFS throughput mode (bursting / provisioned / elastic)"
  type        = string
  default     = "bursting"
}
