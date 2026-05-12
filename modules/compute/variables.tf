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

variable "instance_type" {
  description = "EC2 instance type for vulnerable lab instance"
  type        = string
  default     = "t2.micro"
}

variable "vpc_a_id" {
  description = "VPC A ID from the network module"
  type        = string
}

variable "vpc_a_public_subnet_1_id" {
  description = "Public subnet 1 ID from the network module"
  type        = string
}

variable "vpc_a_public_subnet_2_id" {
  description = "Public subnet 2 ID from the network module"
  type        = string
}

variable "tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {}
}
