resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = merge(local.module_tags, {
    Name = "${var.name_prefix}-vpc-main"
  })
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = merge(local.module_tags, {
    Name = "${var.name_prefix}-igw-main"
  })
}

resource "aws_subnet" "public" {
  count = var.az_count

  vpc_id                  = aws_vpc.main.id
  cidr_block              = local.public_subnet_cidrs[count.index]
  availability_zone       = local.az_names[count.index]
  map_public_ip_on_launch = true

  tags = merge(local.module_tags, {
    Name = "${var.name_prefix}-subnet-public-${local.az_suffixes[count.index]}"
    Tier = "public"
  })
}

resource "aws_subnet" "private_app" {
  count = var.az_count

  vpc_id                  = aws_vpc.main.id
  cidr_block              = local.private_app_subnet_cidrs[count.index]
  availability_zone       = local.az_names[count.index]
  map_public_ip_on_launch = false

  tags = merge(local.module_tags, {
    Name = "${var.name_prefix}-subnet-private-app-${local.az_suffixes[count.index]}"
    Tier = "private-app"
  })
}

resource "aws_subnet" "private_data" {
  count = var.az_count

  vpc_id                  = aws_vpc.main.id
  cidr_block              = local.private_data_subnet_cidrs[count.index]
  availability_zone       = local.az_names[count.index]
  map_public_ip_on_launch = false

  tags = merge(local.module_tags, {
    Name = "${var.name_prefix}-subnet-private-data-${local.az_suffixes[count.index]}"
    Tier = "private-data"
  })
}

resource "aws_eip" "nat" {
  count = var.enable_nat_gateway ? var.az_count : 0

  domain = "vpc"

  tags = merge(local.module_tags, {
    Name = "${var.name_prefix}-eip-nat-${local.az_suffixes[count.index]}"
  })
}

resource "aws_nat_gateway" "main" {
  count = var.enable_nat_gateway ? var.az_count : 0

  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id

  tags = merge(local.module_tags, {
    Name = "${var.name_prefix}-nat-${local.az_suffixes[count.index]}"
  })

  depends_on = [aws_internet_gateway.main]
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  tags = merge(local.module_tags, {
    Name = "${var.name_prefix}-rt-public"
  })
}

resource "aws_route" "public_default" {
  route_table_id         = aws_route_table.public.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.main.id
}

resource "aws_route_table" "private_app" {
  count = var.az_count

  vpc_id = aws_vpc.main.id

  tags = merge(local.module_tags, {
    Name = "${var.name_prefix}-rt-private-app-${local.az_suffixes[count.index]}"
  })
}

resource "aws_route" "private_app_nat" {
  count = var.enable_nat_gateway ? var.az_count : 0

  route_table_id         = aws_route_table.private_app[count.index].id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.main[count.index].id
}

resource "aws_route_table" "private_data" {
  count = var.az_count

  vpc_id = aws_vpc.main.id

  tags = merge(local.module_tags, {
    Name = "${var.name_prefix}-rt-private-data-${local.az_suffixes[count.index]}"
  })
}

resource "aws_route_table_association" "public" {
  count = var.az_count

  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "private_app" {
  count = var.az_count

  subnet_id      = aws_subnet.private_app[count.index].id
  route_table_id = aws_route_table.private_app[count.index].id
}

resource "aws_route_table_association" "private_data" {
  count = var.az_count

  subnet_id      = aws_subnet.private_data[count.index].id
  route_table_id = aws_route_table.private_data[count.index].id
}
