output "vpc_id" {
  description = "ID of the primary VPC."
  value       = module.network.vpc_id
}

output "vpc_cidr" {
  description = "CIDR block of the primary VPC."
  value       = module.network.vpc_cidr
}

output "public_subnet_ids" {
  description = "IDs of public subnets."
  value       = module.network.public_subnet_ids
}

output "private_app_subnet_ids" {
  description = "IDs of private application subnets."
  value       = module.network.private_app_subnet_ids
}

output "private_data_subnet_ids" {
  description = "IDs of private data subnets."
  value       = module.network.private_data_subnet_ids
}

output "app_security_group_id" {
  description = "ID of the application security group."
  value       = module.compute.app_security_group_id
}

output "app_instance_ids" {
  description = "IDs of application instances."
  value       = module.compute.app_instance_ids
}

output "cloudtrail_arn" {
  description = "ARN of the CloudTrail trail."
  value       = module.cloudtrail.cloudtrail_arn
}

output "cloudtrail_log_bucket_name" {
  description = "S3 bucket name storing CloudTrail logs."
  value       = module.cloudtrail.cloudtrail_log_bucket_name
}

output "cloudtrail_kms_key_arn" {
  description = "KMS key ARN used by CloudTrail."
  value       = module.cloudtrail.cloudtrail_kms_key_arn
}

output "config_recorder_name" {
  description = "Name of the AWS Config recorder."
  value       = module.cloudtrail.config_recorder_name
}

output "vpc_flow_log_id" {
  description = "ID of the VPC flow log."
  value       = module.network.vpc_flow_log_id
}

output "storage_data_bucket_name" {
  description = "S3 bucket name used by the storage module."
  value       = module.storage.data_bucket_name
}

output "storage_rds_endpoint" {
  description = "RDS endpoint created by the storage module."
  value       = module.storage.rds_endpoint
}

output "storage_efs_id" {
  description = "EFS file system ID created by the storage module."
  value       = module.storage.efs_id
}

output "monitor_sns_topic_arn" {
  description = "SNS topic ARN used by CIS monitoring alarms."
  value       = module.monitor.cis_monitoring_sns_topic_arn
}

output "monitor_alarm_names" {
  description = "CloudWatch alarm names created by the monitor module."
  value       = module.monitor.cis_monitoring_alarm_names
}
