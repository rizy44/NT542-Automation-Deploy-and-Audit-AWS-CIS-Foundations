# Network Module

This module is part of the root Terraform stack under `infra/`. Use `infra/` as
the supported entry point; running this module directly is only for local module
development.

## Resources

- VPC with DNS support and hostnames enabled.
- Public, private application, and private data subnets across the selected availability zones.
- Internet Gateway, public routing, optional NAT Gateways, private application routing, and isolated private data routing.
- Public and private Network ACLs without broad SSH, RDP, or SMB exposure.
- VPC Flow Logs delivered to CloudWatch Logs.

## Inputs

| Name | Type | Default | Description |
| --- | --- | --- | --- |
| `name_prefix` | `string` | n/a | Prefix used for network resource names. |
| `vpc_cidr` | `string` | n/a | CIDR block for the VPC. |
| `az_count` | `number` | `2` | Number of availability zones to use. Must be at least 2. |
| `enable_nat_gateway` | `bool` | `true` | Whether to create one NAT Gateway per AZ for private app subnet egress. |
| `common_tags` | `map(string)` | n/a | Tags applied to all network resources. |

## Outputs

| Name | Description |
| --- | --- |
| `vpc_id` | ID of the main VPC. |
| `vpc_cidr` | CIDR block of the main VPC. |
| `public_subnet_ids` | IDs of public subnets. |
| `private_app_subnet_ids` | IDs of private application subnets. |
| `private_data_subnet_ids` | IDs of private data subnets. |
| `nat_gateway_ids` | IDs of NAT Gateways, empty when NAT is disabled. |
| `vpc_flow_log_id` | ID of the VPC Flow Log. |
| `vpc_flow_log_group_name` | Name of the CloudWatch Log Group used by VPC Flow Logs. |

## Root Usage

The root stack passes `project_name = "cis-baseline"` and `environment = "dev"` into `local.name_prefix`, then wires network outputs into compute.

```hcl
module "network" {
  source = "./modules/network"

  name_prefix        = local.name_prefix
  vpc_cidr           = var.vpc_cidr
  enable_nat_gateway = var.enable_nat_gateway
  common_tags        = local.common_tags
}
```
