variable "aws_region" {
  description = "AWS region for this stack"
  type        = string
  default     = "ap-southeast-1"
}

variable "environment" {
  description = "Environment label"
  type        = string
  default     = "dev"
}

variable "trail_name" {
  description = "Name of CloudTrail trail"
  type        = string
  default     = "main-cloudtrail"
}

variable "log_bucket_name_prefix" {
  description = "Prefix for CloudTrail log bucket name"
  type        = string
  default     = "cloudtrail-logs"
}

variable "is_multi_region_trail" {
  description = "Whether this trail covers all regions"
  type        = bool
  default     = true
}

variable "include_global_service_events" {
  description = "Include global service events in this trail"
  type        = bool
  default     = true
}

variable "enable_log_file_validation" {
  description = "Enable CloudTrail log file validation"
  type        = bool
  default     = true
}
