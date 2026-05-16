module "network" {
  source = "./modules/network"

  name_prefix        = local.name_prefix
  vpc_cidr           = var.vpc_cidr
  enable_nat_gateway = var.enable_nat_gateway
  enable_flow_logs   = !var.learner_lab_mode
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
  enable_iam_profile = !var.learner_lab_mode
  common_tags        = local.common_tags
}

module "cloudtrail" {
  source = "./modules/cloudtrail"

  name_prefix   = local.name_prefix
  common_tags   = local.common_tags
  enable_config = !var.learner_lab_mode
}

module "storage" {
  source = "./modules/storage"

  environment              = var.environment
  project_name             = var.project_name
  vpc_id                   = module.network.vpc_id
  private_subnet_ids       = module.network.private_data_subnet_ids
  vpc_cidr_block           = module.network.vpc_cidr
  data_bucket_name_prefix  = "${local.name_prefix}-data"
  macie_bucket_name_prefix = "${local.name_prefix}-macie"
  rds_master_password      = var.rds_master_password
  enable_macie             = !var.learner_lab_mode
  enable_rds_monitoring    = !var.learner_lab_mode
}

module "monitor" {
  source = "./modules/monitor"

  environment               = var.environment
  project_name              = var.project_name
  cloudtrail_log_group_name = coalesce(var.cloudtrail_log_group_name, "/aws/cloudtrail/${local.name_prefix}")
  sns_topic_arn             = var.monitor_sns_topic_arn
  sns_topic_name            = var.monitor_sns_topic_name
  alarm_notification_emails = var.monitor_alarm_notification_emails
  metric_namespace          = var.monitor_metric_namespace
  enable_security_hub       = var.enable_security_hub
  enabled_controls          = var.monitor_enabled_controls
  create_metric_filters     = var.monitor_create_metric_filters
}
