locals {
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
