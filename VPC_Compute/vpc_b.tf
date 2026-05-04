# ============================================================================
# VPC B - Partner Environment
# ============================================================================

resource "aws_vpc" "vpc_b" {
  cidr_block           = var.vpc_b_cidr
  enable_dns_support   = var.enable_dns_support
  enable_dns_hostnames = var.enable_dns_hostnames

  tags = merge(
    local.common_tags,
    {
      Name = "${var.project_name}-vpc-b"
    }
  )
}

# ============================================================================
# Private Subnet in VPC B
# ============================================================================

resource "aws_subnet" "vpc_b_private" {
  vpc_id            = aws_vpc.vpc_b.id
  cidr_block        = var.vpc_b_private_subnet_cidr
  availability_zone = local.primary_az

  tags = merge(
    local.common_tags,
    {
      Name = "${var.project_name}-subnet-vpc-b-private"
      Type = "Private"
    }
  )
}

# ============================================================================
# Route Table for VPC B Private Subnet
# ============================================================================

resource "aws_route_table" "vpc_b_private" {
  vpc_id = aws_vpc.vpc_b.id

  tags = merge(
    local.common_tags,
    {
      Name = "${var.project_name}-rt-vpc-b-private"
    }
  )
}

# Route to VPC A via Peering Connection
resource "aws_route" "vpc_b_to_vpc_a" {
  route_table_id            = aws_route_table.vpc_b_private.id
  destination_cidr_block    = var.vpc_a_cidr
  vpc_peering_connection_id = aws_vpc_peering_connection.main.id

  depends_on = [aws_vpc_peering_connection.main]
}

# ============================================================================
# Route Table Association
# ============================================================================

resource "aws_route_table_association" "vpc_b_private" {
  subnet_id      = aws_subnet.vpc_b_private.id
  route_table_id = aws_route_table.vpc_b_private.id
}

# ============================================================================
# VULNERABILITY 6: VPC B Default Security Group
# Intentionally left unchanged to retain default rules
# ============================================================================
# Note: VPC B default security group is NOT modified. It retains its default
# rules which allow all inbound traffic from instances in the same security group.

data "aws_security_group" "vpc_b_default" {
  vpc_id = aws_vpc.vpc_b.id
  name   = "default"

  depends_on = [aws_vpc.vpc_b]
}
