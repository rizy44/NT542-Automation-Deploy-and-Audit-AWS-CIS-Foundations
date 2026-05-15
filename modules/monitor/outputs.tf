output "cis_monitoring_sns_topic_arn" {
  description = "SNS topic ARN used by CIS monitoring alarms"
  value       = local.sns_topic_arn
}

output "cis_monitoring_alarm_names" {
  description = "CloudWatch alarm names created for CIS monitoring controls"
  value       = [for alarm in aws_cloudwatch_metric_alarm.cis : alarm.alarm_name]
}

output "cis_monitoring_filter_names" {
  description = "CloudWatch metric filter names created for CIS monitoring controls"
  value       = [for filter in aws_cloudwatch_log_metric_filter.cis : filter.name]
}

output "security_hub_enabled" {
  description = "Whether AWS Security Hub is enabled by this module"
  value       = length(aws_securityhub_account.this) > 0
}
