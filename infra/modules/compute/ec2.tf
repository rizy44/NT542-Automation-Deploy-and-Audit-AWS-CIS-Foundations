data "aws_ami" "amazon_linux_2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-2023.*-kernel-*-x86_64"]
  }

  filter {
    name   = "architecture"
    values = ["x86_64"]
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

resource "aws_instance" "app" {
  count = length(var.private_subnet_ids)

  ami                         = data.aws_ami.amazon_linux_2023.id
  instance_type               = var.instance_type
  subnet_id                   = var.private_subnet_ids[count.index]
  vpc_security_group_ids      = [aws_security_group.app.id]
  associate_public_ip_address = false
  iam_instance_profile        = var.enable_iam_profile ? aws_iam_instance_profile.app[0].name : null
  monitoring                  = true

  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 1
    instance_metadata_tags      = "enabled"
  }

  root_block_device {
    volume_type           = "gp3"
    volume_size           = 20
    encrypted             = true
    delete_on_termination = true
  }

  tags = merge(local.module_tags, {
    Name = "${var.name_prefix}-ec2-app-${count.index + 1}"
    Tier = "app"
  })
}

# Test instance in peer VPC (VPC B)
resource "aws_instance" "peer" {
  count = var.create_peer_resources ? 1 : 0

  ami                         = data.aws_ami.amazon_linux_2023.id
  instance_type               = var.instance_type
  subnet_id                   = var.peer_private_subnet_id
  vpc_security_group_ids      = var.create_peer_resources ? [aws_security_group.peer[0].id] : []
  associate_public_ip_address = false
  iam_instance_profile        = var.enable_iam_profile ? aws_iam_instance_profile.app[0].name : null
  monitoring                  = true

  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 1
    instance_metadata_tags      = "enabled"
  }

  root_block_device {
    volume_type           = "gp3"
    volume_size           = 20
    encrypted             = true
    delete_on_termination = true
  }

  tags = merge(local.module_tags, {
    Name = "${var.name_prefix}-ec2-peer-1"
    Tier = "peer"
  })
}
