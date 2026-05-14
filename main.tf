terraform {
  cloud {
    organization = "NT542_Automation"

    workspaces {
      name = "aws-cis-foundations"
    }
  }
}

module "network" {
  source = "./modules/network"

  aws_region                     = var.aws_region
  environment                    = var.environment
  project_name                   = var.project_name
  vpc_a_cidr                     = var.vpc_a_cidr
  vpc_a_public_subnet_1_cidr     = var.vpc_a_public_subnet_1_cidr
  vpc_a_private_subnet_1_cidr    = var.vpc_a_private_subnet_1_cidr
  vpc_a_public_subnet_2_cidr     = var.vpc_a_public_subnet_2_cidr
  vpc_a_private_subnet_2_cidr    = var.vpc_a_private_subnet_2_cidr
  vpc_b_cidr                     = var.vpc_b_cidr
  vpc_b_private_subnet_cidr      = var.vpc_b_private_subnet_cidr
  assign_public_ip_public_subnet = var.assign_public_ip_public_subnet
  tags                           = var.tags
}

module "compute" {
  source = "./modules/compute"

  aws_region               = var.aws_region
  environment              = var.environment
  project_name             = var.project_name
  instance_type            = var.instance_type
  vpc_a_id                 = module.network.vpc_a_id
  vpc_a_public_subnet_1_id = module.network.vpc_a_public_subnet_1_id
  vpc_a_public_subnet_2_id = module.network.vpc_a_public_subnet_2_id
  tags                     = var.tags
}

module "storage" {
  source = "./modules/Storage"

  aws_region          = var.aws_region
  environment         = var.environment
  vpc_id              = module.network.vpc_a_id
  private_subnet_ids  = [
    module.network.vpc_a_private_subnet_1_id,
    module.network.vpc_a_private_subnet_2_id
  ]
  vpc_cidr_block      = module.network.vpc_a_cidr

  # passed from a sensitive root input variable (no default, no hardcode)
  rds_master_password = var.rds_master_password
}
