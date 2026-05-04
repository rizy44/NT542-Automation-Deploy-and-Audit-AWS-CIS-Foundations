# ============================================================================
# Outputs - Security Auditing Lab Infrastructure
# ============================================================================

# ============================================================================
# VPC A Outputs
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

# ============================================================================
# VPC A Private Subnet Outputs
# ============================================================================

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

# ============================================================================
# VPC A Route Tables
# ============================================================================

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

# ============================================================================
# VPC B Outputs
# ============================================================================

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

# ============================================================================
# VPC Peering Outputs
# ============================================================================

output "vpc_peering_connection_id" {
  description = "VPC Peering Connection ID"
  value       = aws_vpc_peering_connection.main.id
}

output "vpc_peering_connection_status" {
  description = "Status of VPC Peering Connection"
  value       = aws_vpc_peering_connection_accepter.main.accept_status
}

# ============================================================================
# Network ACL Outputs
# ============================================================================

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

# ============================================================================
# Security Group Outputs
# ============================================================================

output "ec2_security_group_id" {
  description = "Security Group ID for EC2 instance (Vulnerability 3)"
  value       = aws_security_group.ec2_vulnerable.id
}

output "ec2_security_group_rules_summary" {
  description = "Summary of EC2 Security Group rules (Vulnerability 3)"
  value = {
    inbound_ssh_ipv4 = "Allow TCP 22 from 0.0.0.0/0"
    inbound_rdp_ipv4 = "Allow TCP 3389 from 0.0.0.0/0"
    inbound_smb_ipv4 = "Allow TCP 445 from 0.0.0.0/0"
    inbound_ssh_ipv6 = "Allow TCP 22 from ::/0"
    inbound_rdp_ipv6 = "Allow TCP 3389 from ::/0"
    inbound_smb_ipv6 = "Allow TCP 445 from ::/0"
    outbound         = "Allow all traffic (IPv4 and IPv6)"
  }
}

# ============================================================================
# EC2 Instance Outputs - Instance 1
# ============================================================================

output "ec2_instance_1_id" {
  description = "EC2 instance 1 ID (Public Subnet 1, AZ 1)"
  value       = aws_instance.vulnerable[0].id
}

output "ec2_instance_1_private_ip" {
  description = "EC2 instance 1 private IP address"
  value       = aws_instance.vulnerable[0].private_ip
}

output "ec2_instance_1_public_ip" {
  description = "EC2 instance 1 public IP address"
  value       = aws_instance.vulnerable[0].public_ip
}

output "ec2_instance_1_subnet_id" {
  description = "Subnet ID of EC2 instance 1"
  value       = aws_instance.vulnerable[0].subnet_id
}

output "ec2_instance_1_availability_zone" {
  description = "Availability zone of EC2 instance 1"
  value       = aws_instance.vulnerable[0].availability_zone
}

# ============================================================================
# EC2 Instance Outputs - Instance 2
# ============================================================================

output "ec2_instance_2_id" {
  description = "EC2 instance 2 ID (Public Subnet 2, AZ 2)"
  value       = aws_instance.vulnerable[1].id
}

output "ec2_instance_2_private_ip" {
  description = "EC2 instance 2 private IP address"
  value       = aws_instance.vulnerable[1].private_ip
}

output "ec2_instance_2_public_ip" {
  description = "EC2 instance 2 public IP address"
  value       = aws_instance.vulnerable[1].public_ip
}

output "ec2_instance_2_subnet_id" {
  description = "Subnet ID of EC2 instance 2"
  value       = aws_instance.vulnerable[1].subnet_id
}

output "ec2_instance_2_availability_zone" {
  description = "Availability zone of EC2 instance 2"
  value       = aws_instance.vulnerable[1].availability_zone
}

output "ec2_instance_ami_id" {
  description = "AMI ID used for EC2 instance"
  value       = data.aws_ami.amazon_linux_2023.id
}

output "ec2_instance_type" {
  description = "EC2 instance type"
  value       = aws_instance.vulnerable[0].instance_type
}

output "ec2_metadata_options" {
  description = "EC2 metadata configuration (Vulnerability 4 - applied to all instances)"
  value = {
    http_endpoint               = "enabled"
    http_tokens                 = "optional"
    http_put_response_hop_limit = 1
  }
}

output "ec2_root_volume_encrypted" {
  description = "EC2 root volume encryption status (Vulnerability 5 - should be false)"
  value       = "false (unencrypted)"
}

output "ec2_root_volume_size" {
  description = "EC2 root volume size in GiB"
  value       = aws_instance.vulnerable[0].root_block_device[0].volume_size
}

output "ec2_root_volume_type" {
  description = "EC2 root volume type"
  value       = aws_instance.vulnerable[0].root_block_device[0].volume_type
}

# ============================================================================
# Vulnerability Summary Output
# ============================================================================

output "vulnerabilities_summary" {
  description = "Summary of all implemented vulnerabilities (Multi-AZ)"
  value = {
    vulnerability_1 = "NACL: Allow SSH (22) and RDP (3389) from 0.0.0.0/0 - Applied to BOTH Public Subnets"
    vulnerability_2 = "Default SG (VPC A): Left unchanged with permissive default rules"
    vulnerability_3 = "Custom SG: Allow SSH, RDP, SMB from 0.0.0.0/0 and ::/0 - Applied to BOTH EC2 Instances"
    vulnerability_4 = "EC2 Metadata: http_tokens = 'optional' enables IMDSv1 - Applied to BOTH EC2 Instances"
    vulnerability_5 = "EBS Root Volume: Explicitly NOT encrypted (encrypted = false) - Applied to BOTH EC2 Instances"
    vulnerability_6 = "Default SG (VPC B): Left unchanged with permissive default rules"
  }
}

# ============================================================================
# Multi-AZ Deployment Summary
# ============================================================================

output "multi_az_deployment_summary" {
  description = "Summary of Multi-AZ highly available architecture"
  value = {
    vpc_a_public_subnets = {
      subnet_1 = "10.0.1.0/24 (${local.primary_az})"
      subnet_2 = "10.0.3.0/24 (${local.secondary_az})"
    }
    vpc_a_private_subnets = {
      subnet_1 = "10.0.2.0/24 (${local.primary_az})"
      subnet_2 = "10.0.4.0/24 (${local.secondary_az})"
    }
    ec2_instances = {
      instance_1 = "Public Subnet 1 (${local.primary_az})"
      instance_2 = "Public Subnet 2 (${local.secondary_az})"
    }
    routing = {
      public_route_table  = "Shared by both Public Subnets"
      private_route_table = "Shared by both Private Subnets"
      igw_route           = "0.0.0.0/0 → IGW"
      peering_route       = "10.1.0.0/16 → VPC Peering"
    }
  }
}

# ============================================================================
# SSH Connection Strings
# ============================================================================

output "ec2_ssh_commands" {
  description = "SSH connection commands for both EC2 instances"
  value = {
    instance_1 = "ssh -i <key.pem> ec2-user@${aws_instance.vulnerable[0].public_ip}"
    instance_2 = "ssh -i <key.pem> ec2-user@${aws_instance.vulnerable[1].public_ip}"
  }
}

# ============================================================================
# Connectivity Test Information
# ============================================================================

output "connectivity_test_info" {
  description = "Information for testing connectivity between VPCs"
  value = {
    vpc_a_to_vpc_b_route = "10.1.0.0/16 → ${aws_vpc_peering_connection.main.id}"
    vpc_b_to_vpc_a_route = "10.0.0.0/16 → ${aws_vpc_peering_connection.main.id}"
    ec2_instance_1_ssh   = "ssh -i <key.pem> ec2-user@${aws_instance.vulnerable[0].public_ip}"
    ec2_instance_2_ssh   = "ssh -i <key.pem> ec2-user@${aws_instance.vulnerable[1].public_ip}"
  }
}
