variable "environment" {
  description = "Environment label"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name for resource tagging and naming"
  type        = string
  default     = "cis-baseline"
}

variable "cloudtrail_log_group_name" {
  description = "CloudWatch Log Group name that receives CloudTrail events"
  type        = string
}

variable "sns_topic_arn" {
  description = "If provided, use an existing SNS Topic ARN instead of creating a new topic"
  type        = string
  default     = ""
}

variable "sns_topic_name" {
  description = "SNS topic name used by CIS monitoring alarms"
  type        = string
  default     = "cis-monitoring-alerts"
}

variable "alarm_notification_emails" {
  description = "List of email endpoints for SNS alarm notifications. Empty list to skip subscriptions"
  type        = list(string)
  default     = []
}

variable "metric_namespace" {
  description = "CloudWatch metric namespace for CIS filters"
  type        = string
  default     = "CISBenchmark"
}

variable "enable_security_hub" {
  description = "Enable AWS Security Hub for CIS 5.16"
  type        = bool
  default     = false
}

variable "enabled_controls" {
  description = "Optional list of control keys to enable (e.g. [\"unauthorized_api_calls\", \"root_usage\"]). Empty list enables all"
  type        = list(string)
  default     = []
}

variable "create_metric_filters" {
  description = "Set to false to only create SNS topic/subscriptions and skip metric filters/alarms"
  type        = bool
  default     = true
}
