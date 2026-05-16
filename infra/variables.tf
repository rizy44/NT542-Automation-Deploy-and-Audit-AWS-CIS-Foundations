variable "aws_region" {
  description = "AWS region for this stack."
  type        = string
  default     = "ap-southeast-1"
}

variable "project_name" {
  description = "Project name used for resource naming and tagging."
  type        = string
  default     = "cis-baseline"

  validation {
    condition     = can(regex("^[a-z0-9]+(-[a-z0-9]+)*$", var.project_name)) && length(var.project_name) >= 3 && length(var.project_name) <= 16
    error_message = "project_name must be lowercase kebab-case and 3-16 characters long."
  }
}

variable "environment" {
  description = "Environment name used for resource naming and tagging."
  type        = string
  default     = "dev"

  validation {
    condition     = can(regex("^[a-z0-9]+(-[a-z0-9]+)*$", var.environment)) && length(var.environment) >= 3 && length(var.environment) <= 8
    error_message = "environment must be lowercase kebab-case and 3-8 characters long."
  }

  validation {
    condition     = length("${var.project_name}-${var.environment}") <= 20
    error_message = "project_name-environment must be 20 characters or fewer so derived S3 buckets and IAM names stay within AWS limits."
  }
}

variable "owner" {
  description = "Owner tag value applied to managed resources."
  type        = string
  default     = "security-team"
}

variable "cost_center" {
  description = "CostCenter tag value applied to managed resources."
  type        = string
  default     = "security"
}

variable "compliance_scope" {
  description = "Compliance tag value applied to managed resources."
  type        = string
  default     = "cis-aws-foundations"
}

variable "vpc_cidr" {
  description = "CIDR block for the primary VPC."
  type        = string
  default     = "10.0.0.0/16"
}

variable "enable_vpc_peering" {
  description = "Whether to create VPC peering routes between the hub VPC and a spoke VPC."
  type        = bool
  default     = false
}

variable "peer_vpc_id" {
  description = "ID of the spoke/peer VPC to connect to the hub VPC."
  type        = string
  default     = null
  nullable    = true
}

variable "peer_vpc_cidr" {
  description = "CIDR block of the spoke/peer VPC."
  type        = string
  default     = null
  nullable    = true
}

variable "peer_route_table_ids" {
  description = "Route table IDs in the spoke VPC that should receive a return route to the hub VPC."
  type        = list(string)
  default     = []
}

variable "peer_auto_accept" {
  description = "Whether to auto-accept the peering connection. Keep true for same-account, same-region deployments."
  type        = bool
  default     = true
}

variable "enable_nat_gateway" {
  description = "Whether to create NAT gateway resources for private subnet egress."
  type        = bool
  default     = true
}

variable "learner_lab_mode" {
  description = "Disable resources that AWS Learner Lab commonly blocks, such as custom IAM roles and Macie."
  type        = bool
  default     = false
}

variable "admin_cidr_blocks" {
  description = "CIDR blocks allowed administrative access."
  type        = list(string)
  default     = []

  validation {
    condition = alltrue([
      for cidr in var.admin_cidr_blocks :
      can(cidrhost(cidr, 0)) &&
      can(regex("^([0-9]{1,3}\\.){3}[0-9]{1,3}/([0-9]|[12][0-9]|3[0-2])$", cidr)) &&
      cidr != "0.0.0.0/0"
    ])
    error_message = "admin_cidr_blocks must be valid IPv4 CIDRs and cannot include 0.0.0.0/0."
  }
}

variable "instance_type" {
  description = "EC2 instance type for application instances."
  type        = string
  default     = "t3.micro"
}

variable "rds_master_password" {
  description = "Master password for the storage RDS instance. Set with TF_VAR_rds_master_password or a secure Terraform variable."
  type        = string
  sensitive   = true
  nullable    = false

  validation {
    condition     = length(var.rds_master_password) >= 16
    error_message = "rds_master_password must be at least 16 characters."
  }
}

variable "cloudtrail_log_group_name" {
  description = "CloudWatch Log Group name that receives CloudTrail events for CIS monitoring. Defaults to /aws/cloudtrail/<project>-<environment>."
  type        = string
  default     = null
}

variable "monitor_sns_topic_arn" {
  description = "Existing SNS topic ARN for CIS monitoring alarms. Leave empty to create a topic."
  type        = string
  default     = ""
}

variable "monitor_sns_topic_name" {
  description = "SNS topic name used by CIS monitoring alarms."
  type        = string
  default     = "cis-monitoring-alerts"
}

variable "monitor_alarm_notification_emails" {
  description = "Email endpoints for SNS alarm notifications."
  type        = list(string)
  default     = []
}

variable "monitor_metric_namespace" {
  description = "CloudWatch metric namespace for CIS monitoring filters."
  type        = string
  default     = "CISBenchmark"
}

variable "enable_security_hub" {
  description = "Whether to enable AWS Security Hub from the monitor module."
  type        = bool
  default     = false
}

variable "monitor_enabled_controls" {
  description = "Optional list of CIS monitoring control keys to enable. Empty list enables all supported controls."
  type        = list(string)
  default     = []
}

variable "monitor_create_metric_filters" {
  description = "Whether the monitor module should create CloudWatch metric filters and alarms."
  type        = bool
  default     = true
}

variable "tags" {
  description = "Additional tags to merge with baseline common tags."
  type        = map(string)
  default     = {}
}
