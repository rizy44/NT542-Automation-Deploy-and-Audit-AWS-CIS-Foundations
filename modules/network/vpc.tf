# ============================================================================
# VPC A - Main Environment (Multi-AZ)
# ============================================================================

resource "aws_vpc" "vpc_a" {
  cidr_block           = var.vpc_a_cidr
  enable_dns_support   = var.enable_dns_support
  enable_dns_hostnames = var.enable_dns_hostnames

  tags = merge(
    local.common_tags,
    {
      Name = "${var.project_name}-vpc-a"
    }
  )
}

# ============================================================================
# Internet Gateway for VPC A
# ============================================================================

resource "aws_internet_gateway" "vpc_a" {
  vpc_id = aws_vpc.vpc_a.id

  tags = merge(
    local.common_tags,
    {
      Name = "${var.project_name}-igw-a"
    }
  )
}

# ============================================================================
# Public Subnet 1 (AZ 1) in VPC A
# ============================================================================

resource "aws_subnet" "vpc_a_public_1" {
  vpc_id                  = aws_vpc.vpc_a.id
  cidr_block              = var.vpc_a_public_subnet_1_cidr
  map_public_ip_on_launch = var.assign_public_ip_public_subnet
  availability_zone       = local.primary_az

  tags = merge(
    local.common_tags,
    {
      Name = "${var.project_name}-subnet-vpc-a-public-1"
      Type = "Public"
    }
  )
}

# ============================================================================
# Private Subnet 1 (AZ 1) in VPC A
# ============================================================================

resource "aws_subnet" "vpc_a_private_1" {
  vpc_id            = aws_vpc.vpc_a.id
  cidr_block        = var.vpc_a_private_subnet_1_cidr
  availability_zone = local.primary_az

  tags = merge(
    local.common_tags,
    {
      Name = "${var.project_name}-subnet-vpc-a-private-1"
      Type = "Private"
    }
  )
}

# ============================================================================
# Public Subnet 2 (AZ 2) in VPC A
# ============================================================================

resource "aws_subnet" "vpc_a_public_2" {
  vpc_id                  = aws_vpc.vpc_a.id
  cidr_block              = var.vpc_a_public_subnet_2_cidr
  map_public_ip_on_launch = var.assign_public_ip_public_subnet
  availability_zone       = local.secondary_az

  tags = merge(
    local.common_tags,
    {
      Name = "${var.project_name}-subnet-vpc-a-public-2"
      Type = "Public"
    }
  )
}

# ============================================================================
# Private Subnet 2 (AZ 2) in VPC A
# ============================================================================

resource "aws_subnet" "vpc_a_private_2" {
  vpc_id            = aws_vpc.vpc_a.id
  cidr_block        = var.vpc_a_private_subnet_2_cidr
  availability_zone = local.secondary_az

  tags = merge(
    local.common_tags,
    {
      Name = "${var.project_name}-subnet-vpc-a-private-2"
      Type = "Private"
    }
  )
}

# ============================================================================
# Public Route Table (Shared by both public subnets)
# ============================================================================

resource "aws_route_table" "vpc_a_public" {
  vpc_id = aws_vpc.vpc_a.id

  tags = merge(
    local.common_tags,
    {
      Name = "${var.project_name}-rt-vpc-a-public"
    }
  )
}

# ============================================================================
# Private Route Table (Shared by both private subnets)
# ============================================================================

resource "aws_route_table" "vpc_a_private" {
  vpc_id = aws_vpc.vpc_a.id

  tags = merge(
    local.common_tags,
    {
      Name = "${var.project_name}-rt-vpc-a-private"
    }
  )
}

# ============================================================================
# Routes for Public Route Table
# ============================================================================

resource "aws_route" "vpc_a_public_igw" {
  route_table_id         = aws_route_table.vpc_a_public.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.vpc_a.id
}

resource "aws_route" "vpc_a_public_to_vpc_b" {
  route_table_id            = aws_route_table.vpc_a_public.id
  destination_cidr_block    = var.vpc_b_cidr
  vpc_peering_connection_id = aws_vpc_peering_connection.main.id

  depends_on = [aws_vpc_peering_connection.main]
}

# ============================================================================
# Routes for Private Route Table
# ============================================================================

resource "aws_route" "vpc_a_private_to_vpc_b" {
  route_table_id            = aws_route_table.vpc_a_private.id
  destination_cidr_block    = var.vpc_b_cidr
  vpc_peering_connection_id = aws_vpc_peering_connection.main.id

  depends_on = [aws_vpc_peering_connection.main]
}

# ============================================================================
# Route Table Associations - Public Subnets
# ============================================================================

resource "aws_route_table_association" "vpc_a_public_1" {
  subnet_id      = aws_subnet.vpc_a_public_1.id
  route_table_id = aws_route_table.vpc_a_public.id
}

resource "aws_route_table_association" "vpc_a_public_2" {
  subnet_id      = aws_subnet.vpc_a_public_2.id
  route_table_id = aws_route_table.vpc_a_public.id
}

# ============================================================================
# Route Table Associations - Private Subnets
# ============================================================================

resource "aws_route_table_association" "vpc_a_private_1" {
  subnet_id      = aws_subnet.vpc_a_private_1.id
  route_table_id = aws_route_table.vpc_a_private.id
}

resource "aws_route_table_association" "vpc_a_private_2" {
  subnet_id      = aws_subnet.vpc_a_private_2.id
  route_table_id = aws_route_table.vpc_a_private.id
}

# ============================================================================
# VULNERABILITY 2: VPC A Default Security Group
# ============================================================================

data "aws_security_group" "vpc_a_default" {
  vpc_id = aws_vpc.vpc_a.id
  name   = "default"

  depends_on = [aws_vpc.vpc_a]
}