# Terraform CIS Baseline Design

## Goal

Convert the current Terraform folders into a cohesive AWS infrastructure project
that can support CIS AWS Foundations Benchmark work across multiple domains. The
first implementation should replace the vulnerable lab posture with a
production-like, connected network topology and consistent resource naming,
tagging, variables, and outputs.

## Scope

This design covers the initial baseline for:

- Root Terraform composition.
- Network module.
- Compute module.
- CloudTrail and logging module.
- Naming, tagging, and output conventions shared across modules.

It does not implement every CIS control in one pass. The baseline should make
future CIS domains easier to add through dedicated modules such as IAM, S3,
monitoring, and security alarms.

## Architecture

The repository root becomes the main stack. It owns the AWS provider,
environment-level variables, common tags, and module composition.

The stack calls:

- `infra/modules/network`: builds the VPC topology.
- `infra/modules/compute`: deploys private EC2 workloads using network outputs.
- `infra/modules/cloudtrail`: deploys CloudTrail, log buckets, KMS encryption, and
  logging controls, including AWS Config for the first CIS logging baseline.

The current module directories remain, but they become true reusable Terraform
modules rather than independently-run stacks.

## Naming And Tags

All modules use a shared `name_prefix` derived from:

```text
${project_name}-${environment}
```

Resource names follow lowercase, hyphenated, component-oriented names:

- `${name_prefix}-vpc-main`
- `${name_prefix}-subnet-public-a`
- `${name_prefix}-subnet-private-app-a`
- `${name_prefix}-subnet-private-data-a`
- `${name_prefix}-sg-app`
- `${name_prefix}-trail-main`
- `${name_prefix}-bucket-cloudtrail-logs`

Common tags:

- `Project`
- `Environment`
- `ManagedBy`
- `Owner`
- `CostCenter`
- `Compliance`
- `Component`

Each module may add `Component`-specific tags, but it should not redefine the
global tagging model.

## Network Module

The network module creates a realistic single-account baseline:

- One main VPC across two availability zones.
- Public subnets for ingress components such as an ALB and NAT gateways.
- Private app subnets for EC2 workloads.
- Private data subnets reserved for databases or internal services.
- Internet Gateway for public subnets.
- Optional NAT Gateway support for private egress.
- Separate route tables for public, private app, and private data tiers.
- VPC Flow Logs enabled to CloudWatch Logs by default.
- Security groups and NACLs avoid broad management access from `0.0.0.0/0`.

The older two-VPC peering lab topology is replaced by a cleaner baseline. A
future shared-services VPC can be added as a separate module once there is a
real use case for cross-VPC routing.

## Compute Module

The compute module represents private application hosts:

- EC2 instances launch in private app subnets.
- Public IP assignment is disabled.
- IMDSv2 is required.
- Root EBS encryption is enabled.
- Detailed monitoring is enabled by default.
- Security group ingress is restricted to approved sources, such as an ALB
  security group or explicit internal CIDR blocks.
- SSH management access is disabled by default and can be enabled only through
  explicit `admin_cidr_blocks`.
- An IAM instance profile is created with minimal baseline permissions.

The module outputs instance IDs, private IPs, security group IDs, and subnet
placement. It no longer outputs SSH commands to public IPs.

## CloudTrail And Logging Module

The CloudTrail module targets CIS AWS Foundations Benchmark v6 logging controls
4.1 through 4.9:

- Multi-region CloudTrail.
- Global service events included.
- Log file validation enabled.
- Customer managed KMS key with rotation enabled.
- Dedicated CloudTrail log bucket with versioning, encryption, ownership
  controls, and public access block.
- Dedicated S3 access log bucket.
- Server access logging enabled on the CloudTrail log bucket.
- S3 object-level data event logging for read and write events.

AWS Config and VPC Flow Logs are needed for CIS logging controls as well. VPC
Flow Logs belong in the network module because they depend on the VPC. AWS
Config is included in the CloudTrail/logging module for this first baseline in
the active provider region. Full CIS 4.3 coverage across every enabled AWS
region requires a later provider-alias composition or dedicated `infra/modules/config`
implementation that instantiates AWS Config region by region.

## Data Flow

Root stack flow:

1. Root computes `name_prefix` and `common_tags`.
2. Root creates the network module.
3. Root passes private app subnet IDs and VPC ID into compute.
4. Root creates CloudTrail/logging resources independently.
5. Outputs expose stable IDs and names for audit scripts and later modules.

## Error Handling And Validation

Terraform variables should include validation for:

- Non-empty `project_name` and `environment`.
- Valid CIDR block inputs.
- At least two availability zones or two subnet CIDR entries where required.
- Admin CIDR blocks only when management access is explicitly enabled.

The implementation should avoid hard-coded account IDs, regions, and availability
zone names.

## Testing And Verification

Initial verification:

- `terraform fmt -recursive`.
- `terraform validate` in the root stack.
- `terraform validate` for modules if they remain independently valid.
- Static grep checks for old vulnerable values such as public SSH/RDP/SMB ingress,
  `http_tokens = "optional"`, and `encrypted = false`.

AWS-backed verification with `terraform plan` requires valid AWS credentials and
provider/plugin availability.

## Migration Notes

This is a breaking Terraform refactor. Existing state created from the old lab
modules will not automatically map cleanly to the new resource names and
topology. The first implementation should optimize for a clean baseline rather
than state migration.
