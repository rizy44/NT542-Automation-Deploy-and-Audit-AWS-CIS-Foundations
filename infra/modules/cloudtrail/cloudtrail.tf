resource "aws_cloudtrail" "main" {
  name                          = local.cloudtrail_name
  s3_bucket_name                = aws_s3_bucket.cloudtrail_logs.id
  kms_key_id                    = aws_kms_key.cloudtrail.arn
  include_global_service_events = true
  is_multi_region_trail         = true
  enable_log_file_validation    = true
  enable_logging                = true

  dynamic "event_selector" {
    for_each = local.s3_data_event_read_write_type == null ? [] : [local.s3_data_event_read_write_type]

    content {
      read_write_type           = event_selector.value
      include_management_events = true

      data_resource {
        type   = "AWS::S3::Object"
        values = ["arn:${data.aws_partition.current.partition}:s3:::"]
      }
    }
  }

  tags = merge(local.module_tags, {
    Name = local.cloudtrail_name
  })

  depends_on = [
    aws_s3_bucket_policy.cloudtrail_logs,
    aws_s3_bucket_ownership_controls.cloudtrail_logs,
    aws_s3_bucket_server_side_encryption_configuration.cloudtrail_logs,
    aws_s3_bucket_versioning.cloudtrail_logs,
    aws_kms_key.cloudtrail
  ]
}
