output "cloudtrail_arn" {
  description = "ARN of the CloudTrail trail."
  value       = aws_cloudtrail.main.arn
}

output "cloudtrail_home_region" {
  description = "Home region of the CloudTrail trail."
  value       = aws_cloudtrail.main.home_region
}

output "cloudtrail_log_bucket_name" {
  description = "S3 bucket name storing CloudTrail logs."
  value       = aws_s3_bucket.cloudtrail_logs.id
}

output "cloudtrail_access_log_bucket_name" {
  description = "S3 bucket name storing access logs for the CloudTrail log bucket."
  value       = aws_s3_bucket.access_logs.id
}

output "cloudtrail_kms_key_arn" {
  description = "KMS key ARN used by CloudTrail."
  value       = aws_kms_key.cloudtrail.arn
}

output "config_recorder_name" {
  description = "Name of the AWS Config configuration recorder."
  value       = try(aws_config_configuration_recorder.main[0].name, null)
}

output "config_delivery_channel_name" {
  description = "Name of the AWS Config delivery channel."
  value       = try(aws_config_delivery_channel.main[0].name, null)
}

output "config_log_bucket_name" {
  description = "S3 bucket name storing AWS Config delivery snapshots."
  value       = aws_s3_bucket.config_logs.id
}
