# Network Module

This module creates the network layer for the lab:

- VPC A and VPC B
- Public and private subnets
- Internet Gateway and route tables
- VPC peering
- Network ACL for the public subnets
- Default security group lookups for both VPCs

## Inputs

Use the values from `terraform.tfvars.example` as the starting point. The important inputs are:

- `aws_region`
- `environment`
- `project_name`
- `vpc_a_cidr`
- `vpc_b_cidr`
- `vpc_a_public_subnet_1_cidr`
- `vpc_a_public_subnet_2_cidr`
- `vpc_a_private_subnet_1_cidr`
- `vpc_a_private_subnet_2_cidr`
- `vpc_b_private_subnet_cidr`

## Outputs

The module exports the VPC IDs, subnet IDs, route table IDs, peering ID, NACL ID, and default SG IDs needed by the compute module or a root composition layer.

## Usage

This module is intended to be instantiated before `modules/compute` in the same Terraform stack.