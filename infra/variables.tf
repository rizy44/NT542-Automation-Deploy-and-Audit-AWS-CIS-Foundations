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

variable "enable_nat_gateway" {
  description = "Whether to create NAT gateway resources for private subnet egress."
  type        = bool
  default     = true
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

variable "tags" {
  description = "Additional tags to merge with baseline common tags."
  type        = map(string)
  default     = {}
}
