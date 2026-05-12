# Compute Module

This module creates the EC2 layer for the lab:

- Two vulnerable EC2 instances
- The custom security group that exposes SSH, RDP, and SMB
- EC2 metadata and EBS misconfigurations for the audit lab

## Inputs

The compute module expects network outputs from `modules/network`:

- `vpc_a_id`
- `vpc_a_public_subnet_1_id`
- `vpc_a_public_subnet_2_id`

It also accepts the usual tagging and instance parameters:

- `aws_region`
- `environment`
- `project_name`
- `instance_type`

## Outputs

The module exports the instance IDs, public IPs, subnet IDs, security group ID, and vulnerability summaries.

## Usage

Instantiate `modules/network` first, then pass its outputs into this module.
