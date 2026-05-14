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

resource "aws_vpc_security_group_ingress_rule" "app_ssh_admin" {
  for_each = toset(var.admin_cidr_blocks)

  security_group_id = aws_security_group.app.id

  from_port   = 22
  to_port     = 22
  ip_protocol = "tcp"
  cidr_ipv4   = each.value
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
