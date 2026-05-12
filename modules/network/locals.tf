locals {
  account_id   = data.aws_caller_identity.current.account_id
  region_name  = data.aws_region.current.name
  partition    = data.aws_partition.current.partition
  primary_az   = data.aws_availability_zones.available.names[0]
  secondary_az = data.aws_availability_zones.available.names[1]

  common_tags = merge(
    {
      Environment = var.environment
      Project     = var.project_name
      ManagedBy   = "Terraform"
      Purpose     = "CIS-Audit-Vulnerability-Lab"
    },
    var.tags
  )
}