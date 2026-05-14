module "network" {
  source = "./modules/network"

  name_prefix        = local.name_prefix
  vpc_cidr           = var.vpc_cidr
  enable_nat_gateway = var.enable_nat_gateway
  common_tags        = local.common_tags
}

module "compute" {
  source = "./modules/compute"

  name_prefix        = local.name_prefix
  vpc_id             = module.network.vpc_id
  private_subnet_ids = module.network.private_app_subnet_ids
  vpc_cidr           = module.network.vpc_cidr
  admin_cidr_blocks  = var.admin_cidr_blocks
  instance_type      = var.instance_type
  common_tags        = local.common_tags
}

module "cloudtrail" {
  source = "./modules/Cloudtrail"

  name_prefix = local.name_prefix
  common_tags = local.common_tags
}
