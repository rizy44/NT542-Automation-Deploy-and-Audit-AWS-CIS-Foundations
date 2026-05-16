locals {
  hub_route_table_ids = concat(
    aws_route_table.private_app[*].id,
    aws_route_table.private_data[*].id,
  )
}

# Hub-to-spoke peering is intentionally explicit: no transitive routing is
# assumed, and only the CIDR ranges you declare are propagated through the peering link.
resource "aws_vpc_peering_connection" "hub_to_peer" {
  count = var.enable_vpc_peering ? 1 : 0

  vpc_id      = aws_vpc.main.id
  peer_vpc_id = var.peer_vpc_id
  auto_accept = var.peer_auto_accept

  tags = merge(local.module_tags, {
    Name = "${var.name_prefix}-vpc-peering"
  })
}

# Enable DNS resolution across the peering link so private hostnames remain usable
# for hub-and-spoke workload communication.
resource "aws_vpc_peering_connection_options" "requester" {
  count = var.enable_vpc_peering ? 1 : 0

  vpc_peering_connection_id = aws_vpc_peering_connection.hub_to_peer[0].id

  requester {
    allow_remote_vpc_dns_resolution = true
  }

  depends_on = [aws_vpc_peering_connection.hub_to_peer]
}

resource "aws_vpc_peering_connection_options" "accepter" {
  count = var.enable_vpc_peering ? 1 : 0

  vpc_peering_connection_id = aws_vpc_peering_connection.hub_to_peer[0].id

  accepter {
    allow_remote_vpc_dns_resolution = true
  }

  depends_on = [aws_vpc_peering_connection.hub_to_peer]
}

# Route traffic only from private route tables in the hub VPC to the peer VPC CIDR.
# This keeps peering aligned with CIS 6.6 least-access routing.
resource "aws_route" "hub_to_peer" {
  for_each = var.enable_vpc_peering ? toset(local.hub_route_table_ids) : toset([])

  route_table_id            = each.value
  destination_cidr_block    = var.peer_vpc_cidr
  vpc_peering_connection_id = aws_vpc_peering_connection.hub_to_peer[0].id

  depends_on = [aws_vpc_peering_connection_options.requester]
}

# Add the reverse path on the peer side; route table IDs for the spoke VPC are
# injected as inputs so the module stays reusable across accounts and modules.
resource "aws_route" "peer_to_hub" {
  for_each = var.enable_vpc_peering ? toset(var.peer_route_table_ids) : toset([])

  route_table_id            = each.value
  destination_cidr_block    = aws_vpc.main.cidr_block
  vpc_peering_connection_id = aws_vpc_peering_connection.hub_to_peer[0].id

  depends_on = [aws_vpc_peering_connection_options.accepter]
}
