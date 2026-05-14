variable "aws_region" {
  description = "AWS region for this stack"
  type        = string
  default     = "ap-southeast-1"
}

variable "environment" {
  description = "Environment name for resource tagging and naming"
  type        = string
  default     = "lab"
}

variable "project_name" {
  description = "Project name for resource tagging and naming"
  type        = string
  default     = "security-audit"
}

variable "vpc_a_cidr" {
  description = "CIDR block for VPC A (Main Environment)"
  type        = string
  default     = "10.0.0.0/16"
}

variable "vpc_a_public_subnet_1_cidr" {
  description = "CIDR block for VPC A public subnet 1 (AZ 1)"
  type        = string
  default     = "10.0.1.0/24"
}

variable "vpc_a_private_subnet_1_cidr" {
  description = "CIDR block for VPC A private subnet 1 (AZ 1)"
  type        = string
  default     = "10.0.2.0/24"
}

variable "vpc_a_public_subnet_2_cidr" {
  description = "CIDR block for VPC A public subnet 2 (AZ 2)"
  type        = string
  default     = "10.0.3.0/24"
}

variable "vpc_a_private_subnet_2_cidr" {
  description = "CIDR block for VPC A private subnet 2 (AZ 2)"
  type        = string
  default     = "10.0.4.0/24"
}

variable "vpc_b_cidr" {
  description = "CIDR block for VPC B (Partner Environment)"
  type        = string
  default     = "10.1.0.0/16"
}

variable "vpc_b_private_subnet_cidr" {
  description = "CIDR block for VPC B private subnet"
  type        = string
  default     = "10.1.1.0/24"
}

variable "instance_type" {
  description = "EC2 instance type for vulnerable lab instance"
  type        = string
  default     = "t2.micro"
}

variable "rds_master_password" {
  description = "Master password for Storage RDS. Set in Terraform Cloud as a sensitive Terraform variable."
  type        = string
  sensitive   = true
  nullable    = false

  validation {
    condition     = length(var.rds_master_password) >= 16
    error_message = "rds_master_password must be at least 16 characters."
  }
}

variable "assign_public_ip_public_subnet" {
  description = "Enable auto-assign public IPv4 address for VPC A public subnets"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {}
}