# ============================================================================
# Data Source: Latest Amazon Linux 2023 AMI
# ============================================================================

data "aws_ami" "amazon_linux_2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  filter {
    name   = "state"
    values = ["available"]
  }
}

# ============================================================================
# VULNERABILITY 4: EC2 Metadata Options
# Allows both IMDSv1 and IMDSv2 (http_tokens = "optional")
# ============================================================================
# VULNERABILITY 5: EC2 Root EBS Volume - NOT Encrypted
# ============================================================================
# Two EC2 Instances deployed in VPC A Public Subnets (Multi-AZ) with:
# - IMDSv1 enabled via http_tokens = "optional"
# - Root volume explicitly NOT encrypted (encrypted = false)
# ============================================================================

resource "aws_instance" "vulnerable" {
  count         = 2
  ami           = data.aws_ami.amazon_linux_2023.id
  instance_type = var.instance_type

  # Network configuration - alternate between public subnets for HA
  subnet_id                   = count.index == 0 ? aws_subnet.vpc_a_public_1.id : aws_subnet.vpc_a_public_2.id
  security_groups             = [aws_security_group.ec2_vulnerable.id]
  associate_public_ip_address = true

  # ========================================================================
  # VULNERABILITY 4: Metadata Configuration
  # http_tokens = "optional" enables both IMDSv1 and IMDSv2
  # http_endpoint = "enabled" allows metadata service access
  # ========================================================================
  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "optional" # VULNERABILITY: Allows IMDSv1
    http_put_response_hop_limit = 1
    instance_metadata_tags      = "enabled"
  }

  # ========================================================================
  # VULNERABILITY 5: Root EBS Volume - NOT Encrypted
  # Explicitly set encrypted = false to ensure no encryption
  # ========================================================================
  root_block_device {
    volume_type           = "gp3"
    volume_size           = 20
    encrypted             = false # VULNERABILITY: Root volume NOT encrypted
    delete_on_termination = true
  }

  # Monitoring
  monitoring = false

  tags = merge(
    local.common_tags,
    {
      Name            = "${var.project_name}-ec2-vulnerable-${count.index + 1}"
      Instance        = "Instance-${count.index + 1}"
      Vulnerabilities = "4,5"
    }
  )

  depends_on = [
    aws_internet_gateway.vpc_a,
    aws_security_group.ec2_vulnerable
  ]
}
