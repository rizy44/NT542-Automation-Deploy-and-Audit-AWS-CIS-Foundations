# ============================================================================
# VULNERABILITY 1: Network ACL - Allows SSH and RDP from 0.0.0.0/0
# ============================================================================

resource "aws_network_acl" "vpc_a_public" {
  vpc_id     = aws_vpc.vpc_a.id
  subnet_ids = [aws_subnet.vpc_a_public_1.id, aws_subnet.vpc_a_public_2.id]

  tags = merge(
    local.common_tags,
    {
      Name          = "${var.project_name}-nacl-vpc-a-public"
      Vulnerability = "1"
    }
  )
}

resource "aws_network_acl_rule" "vpc_a_inbound_ssh" {
  network_acl_id = aws_network_acl.vpc_a_public.id
  rule_number    = 100
  protocol       = "tcp"
  rule_action    = "allow"
  cidr_block     = "0.0.0.0/0"
  from_port      = 22
  to_port        = 22
}

resource "aws_network_acl_rule" "vpc_a_inbound_rdp" {
  network_acl_id = aws_network_acl.vpc_a_public.id
  rule_number    = 110
  protocol       = "tcp"
  rule_action    = "allow"
  cidr_block     = "0.0.0.0/0"
  from_port      = 3389
  to_port        = 3389
}

resource "aws_network_acl_rule" "vpc_a_inbound_ephemeral" {
  network_acl_id = aws_network_acl.vpc_a_public.id
  rule_number    = 120
  protocol       = "tcp"
  rule_action    = "allow"
  cidr_block     = "0.0.0.0/0"
  from_port      = 1024
  to_port        = 65535
}

resource "aws_network_acl_rule" "vpc_a_outbound_all" {
  network_acl_id = aws_network_acl.vpc_a_public.id
  rule_number    = 100
  protocol       = "-1"
  rule_action    = "allow"
  cidr_block     = "0.0.0.0/0"
  from_port      = 0
  to_port        = 0
  egress         = true
}