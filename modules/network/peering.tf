# ============================================================================
# VPC Peering Connection
# ============================================================================

resource "aws_vpc_peering_connection" "main" {
  vpc_id      = aws_vpc.vpc_a.id
  peer_vpc_id = aws_vpc.vpc_b.id

  tags = merge(
    local.common_tags,
    {
      Name = "${var.project_name}-peering-vpc-a-vpc-b"
    }
  )
}

resource "aws_vpc_peering_connection_accepter" "main" {
  vpc_peering_connection_id = aws_vpc_peering_connection.main.id
  auto_accept               = true

  tags = merge(
    local.common_tags,
    {
      Name = "${var.project_name}-peering-accepter"
    }
  )
}