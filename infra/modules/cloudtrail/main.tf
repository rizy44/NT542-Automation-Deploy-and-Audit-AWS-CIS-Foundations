terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

data "aws_caller_identity" "current" {}

data "aws_partition" "current" {}

data "aws_region" "current" {}

locals {
  cloudtrail_bucket_name = lower("${var.name_prefix}-cloudtrail-${data.aws_caller_identity.current.account_id}-${data.aws_region.current.name}")
  access_log_bucket_name = lower("${var.name_prefix}-s3-access-logs-${data.aws_caller_identity.current.account_id}-${data.aws_region.current.name}")
  config_bucket_name     = lower("${var.name_prefix}-config-${data.aws_caller_identity.current.account_id}-${data.aws_region.current.name}")

  cloudtrail_name = "${var.name_prefix}-trail-main"
  module_tags     = merge(var.common_tags, { Component = "logging" })

  s3_data_event_read_write_type = (
    var.enable_s3_data_event_read_logging && var.enable_s3_data_event_write_logging ? "All" :
    var.enable_s3_data_event_read_logging ? "ReadOnly" :
    var.enable_s3_data_event_write_logging ? "WriteOnly" :
    null
  )
}
