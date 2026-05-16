variable "name_prefix" {
  description = "Prefix used for network resource names."
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC."
  type        = string
}

variable "az_count" {
  description = "Number of availability zones to use."
  type        = number
  default     = 2

  validation {
    condition     = var.az_count >= 2
    error_message = "az_count must be at least 2."
  }
}

variable "enable_nat_gateway" {
  description = "Whether to create one NAT Gateway per AZ for private app subnet egress."
  type        = bool
  default     = true
}

variable "enable_flow_logs" {
  description = "Whether to create VPC Flow Logs and the IAM role required to deliver them."
  type        = bool
  default     = true
}

variable "common_tags" {
  description = "Tags applied to all network resources."
  type        = map(string)
}

variable "enable_vpc_peering" {
  description = "Whether to create a VPC peering connection and route propagation."
  type        = bool
  default     = false
}

variable "peer_vpc_id" {
  description = "ID of the peer VPC to connect to the hub VPC."
  type        = string
  default     = null
  nullable    = true

  validation {
    condition     = !var.enable_vpc_peering || (var.peer_vpc_id != null && length(trimspace(var.peer_vpc_id)) > 0)
    error_message = "peer_vpc_id must be provided when enable_vpc_peering is true."
  }
}

variable "peer_vpc_cidr" {
  description = "CIDR block of the peer VPC. Must not overlap with the hub VPC CIDR."
  type        = string
  default     = null
  nullable    = true

  validation {
    condition     = !var.enable_vpc_peering || (var.peer_vpc_cidr != null && can(cidrhost(var.peer_vpc_cidr, 0)) && var.peer_vpc_cidr != var.vpc_cidr)
    error_message = "peer_vpc_cidr must be provided, valid, and different from the hub VPC CIDR when enable_vpc_peering is true."
  }
}

variable "peer_route_table_ids" {
  description = "Route table IDs in the peer VPC that should receive a route back to the hub VPC."
  type        = list(string)
  default     = []

  validation {
    condition     = !var.enable_vpc_peering || length(var.peer_route_table_ids) > 0
    error_message = "peer_route_table_ids must contain at least one route table when enable_vpc_peering is true."
  }

  validation {
    condition     = alltrue([for route_table_id in var.peer_route_table_ids : length(trimspace(route_table_id)) > 0])
    error_message = "peer_route_table_ids cannot contain empty strings."
  }
}

variable "peer_auto_accept" {
  description = "Whether the peering request should be auto-accepted. Keep true for same-account, same-region peering."
  type        = bool
  default     = true
}
