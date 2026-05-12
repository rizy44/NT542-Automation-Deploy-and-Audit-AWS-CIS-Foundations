# ============================================================================
# VULNERABILITY 3: Custom Security Group - Allows SSH, RDP, SMB from 0.0.0.0/0
# ============================================================================

resource "aws_security_group" "ec2_vulnerable" {
  name_prefix = "${var.project_name}-ec2-"
  description = "Vulnerable security group for CIS audit lab - allows SSH, RDP, SMB from anywhere"
  vpc_id      = var.vpc_a_id

  tags = merge(
    local.common_tags,
    {
      Name          = "${var.project_name}-sg-ec2-vulnerable"
      Vulnerability = "3"
    }
  )
}

resource "aws_vpc_security_group_ingress_rule" "ec2_ssh_ipv4" {
  security_group_id = aws_security_group.ec2_vulnerable.id

  from_port   = 22
  to_port     = 22
  ip_protocol = "tcp"
  cidr_ipv4   = "0.0.0.0/0"

  tags = {
    Name = "Allow SSH from anywhere (IPv4)"
  }
}

resource "aws_vpc_security_group_ingress_rule" "ec2_rdp_ipv4" {
  security_group_id = aws_security_group.ec2_vulnerable.id

  from_port   = 3389
  to_port     = 3389
  ip_protocol = "tcp"
  cidr_ipv4   = "0.0.0.0/0"

  tags = {
    Name = "Allow RDP from anywhere (IPv4)"
  }
}

resource "aws_vpc_security_group_ingress_rule" "ec2_smb_ipv4" {
  security_group_id = aws_security_group.ec2_vulnerable.id

  from_port   = 445
  to_port     = 445
  ip_protocol = "tcp"
  cidr_ipv4   = "0.0.0.0/0"

  tags = {
    Name = "Allow SMB from anywhere (IPv4)"
  }
}

resource "aws_vpc_security_group_ingress_rule" "ec2_ssh_ipv6" {
  security_group_id = aws_security_group.ec2_vulnerable.id

  from_port   = 22
  to_port     = 22
  ip_protocol = "tcp"
  cidr_ipv6   = "::/0"

  tags = {
    Name = "Allow SSH from anywhere (IPv6)"
  }
}

resource "aws_vpc_security_group_ingress_rule" "ec2_rdp_ipv6" {
  security_group_id = aws_security_group.ec2_vulnerable.id

  from_port   = 3389
  to_port     = 3389
  ip_protocol = "tcp"
  cidr_ipv6   = "::/0"

  tags = {
    Name = "Allow RDP from anywhere (IPv6)"
  }
}

resource "aws_vpc_security_group_ingress_rule" "ec2_smb_ipv6" {
  security_group_id = aws_security_group.ec2_vulnerable.id

  from_port   = 445
  to_port     = 445
  ip_protocol = "tcp"
  cidr_ipv6   = "::/0"

  tags = {
    Name = "Allow SMB from anywhere (IPv6)"
  }
}

resource "aws_vpc_security_group_egress_rule" "ec2_all_outbound" {
  security_group_id = aws_security_group.ec2_vulnerable.id

  from_port   = -1
  to_port     = -1
  ip_protocol = "-1"
  cidr_ipv4   = "0.0.0.0/0"

  tags = {
    Name = "Allow all outbound traffic"
  }
}

resource "aws_vpc_security_group_egress_rule" "ec2_all_outbound_ipv6" {
  security_group_id = aws_security_group.ec2_vulnerable.id

  from_port   = -1
  to_port     = -1
  ip_protocol = "-1"
  cidr_ipv6   = "::/0"

  tags = {
    Name = "Allow all outbound traffic (IPv6)"
  }
}
