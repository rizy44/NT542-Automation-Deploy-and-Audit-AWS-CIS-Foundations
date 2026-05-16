variable "name_prefix" {
  description = "Prefix used for network resource names."
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC."
  type        = string
}

variable "az_count" {
  description = "Number of availability zones to use."
  type        = number
  default     = 2

  validation {
    condition     = var.az_count >= 2
    error_message = "az_count must be at least 2."
  }
}

variable "enable_nat_gateway" {
  description = "Whether to create one NAT Gateway per AZ for private app subnet egress."
  type        = bool
  default     = true
}

variable "enable_flow_logs" {
  description = "Whether to create VPC Flow Logs and the IAM role required to deliver them."
  type        = bool
  default     = true
}

variable "common_tags" {
  description = "Tags applied to all network resources."
  type        = map(string)
}
