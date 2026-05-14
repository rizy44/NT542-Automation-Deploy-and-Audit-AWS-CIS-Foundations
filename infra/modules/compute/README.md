# Compute Module

This module is part of the root Terraform stack under `infra/`. Use `infra/` as
the supported entry point; running this module directly is only for local module
development.

## Resources

- Private Amazon Linux 2023 application instances in supplied private subnets.
- Application security group with HTTP access from the VPC CIDR.
- Optional SSH ingress only for explicit administrator CIDR blocks.
- IAM role and instance profile for AWS Systems Manager access.

## Inputs

| Name | Type | Default | Description |
| --- | --- | --- | --- |
| `name_prefix` | `string` | n/a | Prefix used for compute resource names. |
| `vpc_id` | `string` | n/a | VPC ID where compute resources are created. |
| `vpc_cidr` | `string` | n/a | CIDR block for internal VPC application access. |
| `private_subnet_ids` | `list(string)` | n/a | Private subnet IDs for app instances. Must contain at least one subnet. |
| `instance_type` | `string` | `"t3.micro"` | EC2 instance type for app instances. |
| `admin_cidr_blocks` | `list(string)` | `[]` | Optional administrator CIDR blocks allowed to SSH. |
| `common_tags` | `map(string)` | n/a | Common tags to apply to compute resources. |

## Outputs

| Name | Description |
| --- | --- |
| `app_security_group_id` | Security group ID for app instances. |
| `app_instance_ids` | IDs of app instances. |
| `app_instance_private_ips` | Private IP addresses of app instances. |
| `app_instance_subnet_ids` | Subnet IDs used by app instances. |
| `app_instance_profile_name` | IAM instance profile name attached to app instances. |
| `app_instance_role_name` | IAM role name used by app instances. |

## Root Usage

The root stack deploys compute into `module.network.private_app_subnet_ids` so instances stay private.

```hcl
module "compute" {
  source = "./modules/compute"

  name_prefix        = local.name_prefix
  vpc_id             = module.network.vpc_id
  private_subnet_ids = module.network.private_app_subnet_ids
  vpc_cidr           = module.network.vpc_cidr
  admin_cidr_blocks  = var.admin_cidr_blocks
  instance_type      = var.instance_type
  common_tags        = local.common_tags
}
```
