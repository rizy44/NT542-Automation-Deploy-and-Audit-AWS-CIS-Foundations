terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

data "aws_caller_identity" "current" {}

data "aws_partition" "current" {}

data "aws_region" "current" {}

locals {
  data_bucket_name  = lower("${var.data_bucket_name_prefix}-${data.aws_caller_identity.current.account_id}-${data.aws_region.current.name}")
  macie_bucket_name = lower("${var.macie_bucket_name_prefix}-${data.aws_caller_identity.current.account_id}-${data.aws_region.current.name}")

  common_tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
    Project     = "Storage"
  }
}