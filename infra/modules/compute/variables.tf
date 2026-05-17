variable "name_prefix" {
  description = "Prefix used for compute resource names."
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where compute resources are created."
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block for internal VPC application access."
  type        = string
}

variable "private_subnet_ids" {
  description = "Private subnet IDs for app instances."
  type        = list(string)

  validation {
    condition     = length(var.private_subnet_ids) > 0
    error_message = "private_subnet_ids must contain at least one subnet ID."
  }
}

variable "instance_type" {
  description = "EC2 instance type for app instances."
  type        = string
  default     = "t3.micro"
}

variable "enable_iam_profile" {
  description = "Whether to create and attach an IAM instance profile for app instances."
  type        = bool
  default     = true
}

variable "admin_cidr_blocks" {
  description = "Optional administrator CIDR blocks allowed to SSH to app instances."
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

variable "common_tags" {
  description = "Common tags to apply to compute resources."
  type        = map(string)
}

variable "peer_vpc_id" {
  description = "Optional peer VPC ID (spoke) for test instance placement."
  type        = string
  default     = ""
  nullable    = true
}

variable "peer_private_subnet_id" {
  description = "Optional private subnet ID in the peer VPC for test instance placement."
  type        = string
  default     = ""
  nullable    = true
}

variable "peer_vpc_cidr" {
  description = "CIDR block of the peer VPC."
  type        = string
  default     = ""
  nullable    = true
}

variable "create_peer_resources" {
  description = "Whether to create peer test resources (SG and EC2) in the peer VPC."
  type        = bool
  default     = false
}
