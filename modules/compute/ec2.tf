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
# ============================================================================
# VULNERABILITY 5: EC2 Root EBS Volume - NOT Encrypted
# ============================================================================

resource "aws_instance" "vulnerable" {
  count         = 2
  ami           = data.aws_ami.amazon_linux_2023.id
  instance_type = var.instance_type

  subnet_id                   = count.index == 0 ? var.vpc_a_public_subnet_1_id : var.vpc_a_public_subnet_2_id
  security_groups             = [aws_security_group.ec2_vulnerable.id]
  associate_public_ip_address = true

  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "optional"
    http_put_response_hop_limit = 1
    instance_metadata_tags      = "enabled"
  }

  root_block_device {
    volume_type           = "gp3"
    volume_size           = 20
    encrypted             = false
    delete_on_termination = true
  }

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
    aws_security_group.ec2_vulnerable
  ]
}
