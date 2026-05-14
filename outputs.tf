output "vpc_a_id" {
  description = "VPC A ID"
  value       = module.network.vpc_a_id
}

output "vpc_b_id" {
  description = "VPC B ID"
  value       = module.network.vpc_b_id
}

output "vpc_peering_connection_id" {
  description = "VPC Peering Connection ID"
  value       = module.network.vpc_peering_connection_id
}

output "ec2_instance_1_id" {
  description = "EC2 instance 1 ID"
  value       = module.compute.ec2_instance_1_id
}

output "ec2_instance_1_public_ip" {
  description = "EC2 instance 1 public IP"
  value       = module.compute.ec2_instance_1_public_ip
}

output "ec2_instance_2_id" {
  description = "EC2 instance 2 ID"
  value       = module.compute.ec2_instance_2_id
}

output "ec2_instance_2_public_ip" {
  description = "EC2 instance 2 public IP"
  value       = module.compute.ec2_instance_2_public_ip
}

output "ec2_security_group_id" {
  description = "EC2 security group ID"
  value       = module.compute.ec2_security_group_id
}

output "vpc_a_public_subnet_1_id" {
  description = "VPC A public subnet 1 ID"
  value       = module.network.vpc_a_public_subnet_1_id
}

output "vpc_a_public_subnet_2_id" {
  description = "VPC A public subnet 2 ID"
  value       = module.network.vpc_a_public_subnet_2_id
}

output "storage_data_bucket_name" {
  description = "Storage module data bucket name"
  value       = module.storage.data_bucket_name
}

output "storage_rds_endpoint" {
  description = "Storage module RDS endpoint"
  value       = module.storage.rds_endpoint
}

output "storage_efs_id" {
  description = "Storage module EFS ID"
  value       = module.storage.efs_id
}
