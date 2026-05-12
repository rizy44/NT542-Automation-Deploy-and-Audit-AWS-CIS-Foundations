# ============================================================================
# Outputs - Network Infrastructure
# ============================================================================

output "vpc_a_id" {
  description = "VPC A (Main Environment) ID"
  value       = aws_vpc.vpc_a.id
}

output "vpc_a_cidr" {
  description = "VPC A CIDR block"
  value       = aws_vpc.vpc_a.cidr_block
}

output "vpc_a_public_subnet_1_id" {
  description = "VPC A public subnet 1 (AZ 1) ID"
  value       = aws_subnet.vpc_a_public_1.id
}

output "vpc_a_public_subnet_1_cidr" {
  description = "VPC A public subnet 1 CIDR block"
  value       = aws_subnet.vpc_a_public_1.cidr_block
}

output "vpc_a_public_subnet_1_az" {
  description = "VPC A public subnet 1 availability zone"
  value       = aws_subnet.vpc_a_public_1.availability_zone
}

output "vpc_a_public_subnet_2_id" {
  description = "VPC A public subnet 2 (AZ 2) ID"
  value       = aws_subnet.vpc_a_public_2.id
}

output "vpc_a_public_subnet_2_cidr" {
  description = "VPC A public subnet 2 CIDR block"
  value       = aws_subnet.vpc_a_public_2.cidr_block
}

output "vpc_a_public_subnet_2_az" {
  description = "VPC A public subnet 2 availability zone"
  value       = aws_subnet.vpc_a_public_2.availability_zone
}

output "vpc_a_private_subnet_1_id" {
  description = "VPC A private subnet 1 (AZ 1) ID"
  value       = aws_subnet.vpc_a_private_1.id
}

output "vpc_a_private_subnet_1_cidr" {
  description = "VPC A private subnet 1 CIDR block"
  value       = aws_subnet.vpc_a_private_1.cidr_block
}

output "vpc_a_private_subnet_2_id" {
  description = "VPC A private subnet 2 (AZ 2) ID"
  value       = aws_subnet.vpc_a_private_2.id
}

output "vpc_a_private_subnet_2_cidr" {
  description = "VPC A private subnet 2 CIDR block"
  value       = aws_subnet.vpc_a_private_2.cidr_block
}

output "vpc_a_public_route_table_id" {
  description = "Route table ID for VPC A public subnets (shared)"
  value       = aws_route_table.vpc_a_public.id
}

output "vpc_a_private_route_table_id" {
  description = "Route table ID for VPC A private subnets (shared)"
  value       = aws_route_table.vpc_a_private.id
}

output "vpc_a_internet_gateway_id" {
  description = "Internet Gateway ID for VPC A"
  value       = aws_internet_gateway.vpc_a.id
}

output "vpc_a_route_table_id" {
  description = "Route table ID for VPC A public subnets (shared)"
  value       = aws_route_table.vpc_a_public.id
}

output "vpc_a_default_sg_id" {
  description = "VPC A default security group ID"
  value       = data.aws_security_group.vpc_a_default.id
}

output "vpc_b_id" {
  description = "VPC B (Partner Environment) ID"
  value       = aws_vpc.vpc_b.id
}

output "vpc_b_cidr" {
  description = "VPC B CIDR block"
  value       = aws_vpc.vpc_b.cidr_block
}

output "vpc_b_private_subnet_id" {
  description = "VPC B private subnet ID"
  value       = aws_subnet.vpc_b_private.id
}

output "vpc_b_private_subnet_cidr" {
  description = "VPC B private subnet CIDR block"
  value       = aws_subnet.vpc_b_private.cidr_block
}

output "vpc_b_route_table_id" {
  description = "Route table ID for VPC B private subnet"
  value       = aws_route_table.vpc_b_private.id
}

output "vpc_b_default_sg_id" {
  description = "VPC B default security group ID"
  value       = data.aws_security_group.vpc_b_default.id
}

output "vpc_peering_connection_id" {
  description = "VPC Peering Connection ID"
  value       = aws_vpc_peering_connection.main.id
}

output "vpc_peering_connection_status" {
  description = "Status of VPC Peering Connection"
  value       = aws_vpc_peering_connection_accepter.main.accept_status
}

output "vpc_a_nacl_id" {
  description = "Network ACL ID for VPC A public subnet"
  value       = aws_network_acl.vpc_a_public.id
}

output "vpc_a_nacl_rules_summary" {
  description = "Summary of NACL rules (Vulnerability 1)"
  value = {
    inbound_ssh       = "Allow TCP 22 from 0.0.0.0/0"
    inbound_rdp       = "Allow TCP 3389 from 0.0.0.0/0"
    inbound_ephemeral = "Allow TCP 1024-65535 from 0.0.0.0/0"
    outbound          = "Allow all traffic"
    applies_to        = "Both Public Subnet 1 (AZ 1) and Public Subnet 2 (AZ 2)"
  }
}

output "network_vulnerabilities_summary" {
  description = "Summary of network-side vulnerabilities"
  value = {
    vulnerability_1 = "NACL: Allow SSH (22) and RDP (3389) from 0.0.0.0/0 - Applied to BOTH Public Subnets"
    vulnerability_2 = "Default SG (VPC A): Left unchanged with permissive default rules"
    vulnerability_6 = "Default SG (VPC B): Left unchanged with permissive default rules"
  }
}

output "network_topology_summary" {
  description = "Summary of the network topology"
  value = {
    vpc_a_public_subnets = {
      subnet_1 = "10.0.1.0/24 (${local.primary_az})"
      subnet_2 = "10.0.3.0/24 (${local.secondary_az})"
    }
    vpc_a_private_subnets = {
      subnet_1 = "10.0.2.0/24 (${local.primary_az})"
      subnet_2 = "10.0.4.0/24 (${local.secondary_az})"
    }
    routing = {
      public_route_table  = "Shared by both Public Subnets"
      private_route_table = "Shared by both Private Subnets"
      igw_route           = "0.0.0.0/0 → IGW"
      peering_route       = "10.1.0.0/16 → VPC Peering"
    }
    peer_vpc = {
      cidr = "10.1.0.0/16"
      subnet = "10.1.1.0/24"
    }
  }
}