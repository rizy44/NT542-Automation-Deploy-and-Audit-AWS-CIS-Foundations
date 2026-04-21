resource "aws_cloudtrail" "this" {
  name                          = var.trail_name
  s3_bucket_name                = aws_s3_bucket.cloudtrail_logs.id
  kms_key_id                    = aws_kms_key.cloudtrail.arn
  include_global_service_events = var.include_global_service_events
  is_multi_region_trail         = var.is_multi_region_trail
  enable_log_file_validation    = var.enable_log_file_validation
  enable_logging                = true

  tags = merge(local.common_tags, {
    Name = var.trail_name
  })

  depends_on = [
    aws_s3_bucket_policy.cloudtrail_logs,
    aws_kms_key.cloudtrail
  ]
}
