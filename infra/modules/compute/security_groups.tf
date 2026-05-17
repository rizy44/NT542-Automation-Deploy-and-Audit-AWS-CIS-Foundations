resource "aws_security_group" "app" {
  name        = "${var.name_prefix}-sg-app"
  description = "production-like app SG"
  vpc_id      = var.vpc_id

  tags = merge(local.module_tags, {
    Name = "${var.name_prefix}-sg-app"
  })
}

resource "aws_vpc_security_group_ingress_rule" "app_http" {
  security_group_id = aws_security_group.app.id

  from_port   = 80
  to_port     = 80
  ip_protocol = "tcp"
  cidr_ipv4   = var.vpc_cidr
}

resource "aws_vpc_security_group_ingress_rule" "app_smb_vpc_only" {
  security_group_id = aws_security_group.app.id

  from_port   = 445
  to_port     = 445
  ip_protocol = "tcp"
  cidr_ipv4   = var.vpc_cidr
}

resource "aws_vpc_security_group_egress_rule" "app_all_ipv4" {
  security_group_id = aws_security_group.app.id

  ip_protocol = "-1"
  cidr_ipv4   = "0.0.0.0/0"
}

resource "aws_vpc_security_group_egress_rule" "app_all_ipv6" {
  security_group_id = aws_security_group.app.id

  ip_protocol = "-1"
  cidr_ipv6   = "::/0"
}

# Security group for peer VPC (VPC B) test instance
resource "aws_security_group" "peer" {
  count       = var.create_peer_resources ? 1 : 0
  name        = "${var.name_prefix}-sg-peer"
  description = "Security group in VPC B allowing ICMP and SSH from VPC A"
  vpc_id      = var.peer_vpc_id

  tags = merge(local.module_tags, {
    Name = "${var.name_prefix}-sg-peer"
  })
}

resource "aws_security_group_rule" "peer_icmp_in" {
  count             = var.create_peer_resources ? 1 : 0
  type              = "ingress"
  from_port         = -1
  to_port           = -1
  protocol          = "icmp"
  cidr_blocks       = [var.vpc_cidr]
  security_group_id = aws_security_group.peer[0].id
}

resource "aws_security_group_rule" "peer_ssh_in" {
  count             = var.create_peer_resources ? 1 : 0
  type              = "ingress"
  from_port         = 22
  to_port           = 22
  protocol          = "tcp"
  cidr_blocks       = [var.vpc_cidr]
  security_group_id = aws_security_group.peer[0].id
}

resource "aws_security_group_rule" "peer_egress_all" {
  count             = var.create_peer_resources ? 1 : 0
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  cidr_blocks       = ["0.0.0.0/0"]
  ipv6_cidr_blocks  = ["::/0"]
  security_group_id = aws_security_group.peer[0].id
}
