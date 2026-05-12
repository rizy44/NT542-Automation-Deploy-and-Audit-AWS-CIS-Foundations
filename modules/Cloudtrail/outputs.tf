output "cloudtrail_arn" {
  description = "ARN of the CloudTrail trail"
  value       = aws_cloudtrail.this.arn
}

output "cloudtrail_home_region" {
  description = "Home region of the CloudTrail trail"
  value       = aws_cloudtrail.this.home_region
}

output "cloudtrail_log_bucket_name" {
  description = "S3 bucket name storing CloudTrail logs"
  value       = aws_s3_bucket.cloudtrail_logs.id
}

output "cloudtrail_kms_key_arn" {
  description = "KMS key ARN used by CloudTrail"
  value       = aws_kms_key.cloudtrail.arn
}
