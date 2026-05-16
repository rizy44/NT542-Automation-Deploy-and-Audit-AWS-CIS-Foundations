output "vpc_id" {
  description = "ID of the main VPC."
  value       = aws_vpc.main.id
}

output "vpc_cidr" {
  description = "CIDR block of the main VPC."
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_ids" {
  description = "IDs of public subnets."
  value       = aws_subnet.public[*].id
}

output "private_app_subnet_ids" {
  description = "IDs of private application subnets."
  value       = aws_subnet.private_app[*].id
}

output "private_data_subnet_ids" {
  description = "IDs of private data subnets."
  value       = aws_subnet.private_data[*].id
}

output "nat_gateway_ids" {
  description = "IDs of NAT Gateways, empty when NAT is disabled."
  value       = aws_nat_gateway.main[*].id
}

output "vpc_flow_log_id" {
  description = "ID of the VPC Flow Log."
  value       = try(aws_flow_log.main[0].id, null)
}

output "vpc_flow_log_group_name" {
  description = "Name of the CloudWatch Log Group used by VPC Flow Logs."
  value       = try(aws_cloudwatch_log_group.vpc_flow_logs[0].name, null)
}

output "vpc_peering_connection_id" {
  description = "ID of the hub-to-peer VPC peering connection, if enabled."
  value       = try(aws_vpc_peering_connection.hub_to_peer[0].id, null)
}
