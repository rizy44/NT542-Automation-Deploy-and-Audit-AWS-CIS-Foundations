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

output "ec2_instance_1_id" {
  description = "EC2 instance 1 ID (Public Subnet 1)"
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

output "ec2_instance_2_id" {
  description = "EC2 instance 2 ID (Public Subnet 2)"
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

output "compute_vulnerabilities_summary" {
  description = "Summary of compute-side vulnerabilities"
  value = {
    vulnerability_3 = "Custom SG: Allow SSH, RDP, SMB from 0.0.0.0/0 and ::/0 - Applied to BOTH EC2 Instances"
    vulnerability_4 = "EC2 Metadata: http_tokens = 'optional' enables IMDSv1 - Applied to BOTH EC2 Instances"
    vulnerability_5 = "EBS Root Volume: Explicitly NOT encrypted (encrypted = false) - Applied to BOTH EC2 Instances"
  }
}

output "ec2_ssh_commands" {
  description = "SSH connection commands for both EC2 instances"
  value = {
    instance_1 = "ssh -i <key.pem> ec2-user@${aws_instance.vulnerable[0].public_ip}"
    instance_2 = "ssh -i <key.pem> ec2-user@${aws_instance.vulnerable[1].public_ip}"
  }
}
