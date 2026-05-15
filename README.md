# Terraform CIS Baseline

Terraform stack for a concise CIS-oriented AWS baseline. The supported Terraform
entry point is `infra/`; direct module runs are for local module development
only.

## Topology

- VPC with public, private application, and private data subnets.
- Private EC2 application instances deployed into private application subnets.
- CloudTrail with KMS-encrypted S3 logging and log file validation.
- AWS Config delivery resources in the active provider region.
- VPC Flow Logs delivered to CloudWatch Logs.

## Quick Start

```bash
cd infra
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform fmt -recursive
terraform validate
terraform plan
```

## Key Inputs

- `aws_region`: AWS region for the stack.
- `project_name`: Project name used for names and tags. Default: `cis-baseline`.
- `environment`: Environment name used for names and tags. Default: `dev`.
- `vpc_cidr`: CIDR block for the primary VPC.
- `enable_nat_gateway`: Whether private application subnets get NAT egress.
- `admin_cidr_blocks`: Optional administrator CIDRs for SSH; leave empty to use SSM access.
- `instance_type`: EC2 instance type for private app instances.
- `tags`: Additional tags merged with baseline tags.

## Modules

- `infra/modules/network`: VPC, public/private subnets, routing, NACLs, NAT, and VPC Flow Logs.
- `infra/modules/compute`: Private EC2 app instances, security group, and SSM IAM profile.
- `infra/modules/cloudtrail`: CloudTrail, KMS, S3 log buckets, and AWS Config resources.
- `infra/modules/monitor`: CloudWatch metric filters, alarms, SNS notifications, and Security Hub controls.
- `infra/modules/storage`: S3, Macie, RDS, EFS, and storage encryption controls.

## Current CIS Coverage Note

CloudTrail is configured as a multi-region trail, but AWS Config is a regional
service. This baseline enables AWS Config in the active provider region only.
Full CIS 4.3 coverage for every enabled AWS region requires a later root
provider-alias composition or dedicated multi-region Config module.
