locals {
  az_names    = slice(data.aws_availability_zones.available.names, 0, var.az_count)
  az_suffixes = [for az_name in local.az_names : substr(az_name, length(az_name) - 1, 1)]

  public_subnet_cidrs       = [for index, az_name in local.az_names : cidrsubnet(var.vpc_cidr, 8, index)]
  private_app_subnet_cidrs  = [for index, az_name in local.az_names : cidrsubnet(var.vpc_cidr, 8, index + 10)]
  private_data_subnet_cidrs = [for index, az_name in local.az_names : cidrsubnet(var.vpc_cidr, 8, index + 20)]

  module_tags = merge(
    var.common_tags,
    {
      Component = "network"
    }
  )
}
