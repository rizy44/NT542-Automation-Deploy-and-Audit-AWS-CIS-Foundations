# Terraform CIS Baseline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor the Terraform project into a connected, production-like AWS baseline that supports CIS AWS Foundations Benchmark work.

**Architecture:** The repository root becomes the deployable Terraform stack. It composes focused `network`, `compute`, and `cloudtrail` modules using one naming/tagging model and passes outputs between modules. Network creates the VPC topology and VPC Flow Logs, compute deploys private hardened EC2 instances, and CloudTrail/logging creates audit logging, AWS Config, KMS, and S3 data event controls.

**Tech Stack:** Terraform `>= 1.5.0`, AWS provider `~> 5.0`, AWS VPC, EC2, IAM, CloudTrail, CloudWatch Logs, KMS, S3, AWS Config.

---

## File Structure

- Create `providers.tf`: root Terraform and AWS provider configuration.
- Create `variables.tf`: root environment variables and validations.
- Create `locals.tf`: root `name_prefix` and `common_tags`.
- Create `main.tf`: root module composition.
- Create `outputs.tf`: root outputs for VPC, compute, and logging.
- Create `terraform.tfvars.example`: root example values.
- Modify `infra/modules/network/*.tf`: convert network to a reusable VPC module with realistic subnets, route tables, NAT option, and VPC Flow Logs.
- Modify `infra/modules/compute/*.tf`: convert compute to private hardened EC2 workloads.
- Modify `infra/modules/cloudtrail/*.tf`: add S3 access logging, ownership controls, CloudTrail data events, AWS Config, and consistent naming.
- Modify module READMEs and examples to reflect root-driven usage.

---

### Task 1: Root Stack Composition

**Files:**
- Create: `providers.tf`
- Create: `variables.tf`
- Create: `locals.tf`
- Create: `main.tf`
- Create: `outputs.tf`
- Create: `terraform.tfvars.example`

- [ ] **Step 1: Create root provider configuration**

Create `providers.tf` with:

```hcl
terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = local.common_tags
  }
}
```

- [ ] **Step 2: Create root variables**

Create `variables.tf` with validated project inputs:

```hcl
variable "aws_region" {
  description = "AWS region for the baseline stack."
  type        = string
  default     = "ap-southeast-1"
}

variable "project_name" {
  description = "Short project name used in resource names."
  type        = string
  default     = "cis-baseline"

  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9-]{1,30}[a-z0-9]$", var.project_name))
    error_message = "project_name must be lowercase kebab-case, 3-32 characters, and contain only letters, numbers, and hyphens."
  }
}

variable "environment" {
  description = "Environment name used in resource names and tags."
  type        = string
  default     = "dev"

  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9-]{1,18}[a-z0-9]$", var.environment))
    error_message = "environment must be lowercase kebab-case, 3-20 characters, and contain only letters, numbers, and hyphens."
  }
}

variable "owner" {
  description = "Owner tag value."
  type        = string
  default     = "security-team"
}

variable "cost_center" {
  description = "CostCenter tag value."
  type        = string
  default     = "security"
}

variable "compliance_scope" {
  description = "Compliance tag value."
  type        = string
  default     = "cis-aws-foundations"
}

variable "vpc_cidr" {
  description = "CIDR block for the main VPC."
  type        = string
  default     = "10.0.0.0/16"
}

variable "enable_nat_gateway" {
  description = "Create NAT gateways for private subnet egress."
  type        = bool
  default     = true
}

variable "admin_cidr_blocks" {
  description = "CIDR blocks allowed to reach admin ports when admin access is enabled."
  type        = list(string)
  default     = []
}

variable "instance_type" {
  description = "EC2 instance type for private application instances."
  type        = string
  default     = "t3.micro"
}

variable "tags" {
  description = "Additional tags applied to all resources."
  type        = map(string)
  default     = {}
}
```

- [ ] **Step 3: Create root locals**

Create `locals.tf` with:

```hcl
locals {
  name_prefix = "${var.project_name}-${var.environment}"

  common_tags = merge(
    {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
      Owner       = var.owner
      CostCenter  = var.cost_center
      Compliance  = var.compliance_scope
    },
    var.tags
  )
}
```

- [ ] **Step 4: Compose modules in root `main.tf`**

Create `main.tf` with:

```hcl
module "network" {
  source = "./infra/modules/network"

  name_prefix        = local.name_prefix
  vpc_cidr           = var.vpc_cidr
  enable_nat_gateway = var.enable_nat_gateway
  common_tags        = local.common_tags
}

module "compute" {
  source = "./infra/modules/compute"

  name_prefix        = local.name_prefix
  vpc_id             = module.network.vpc_id
  private_subnet_ids = module.network.private_app_subnet_ids
  vpc_cidr           = module.network.vpc_cidr
  admin_cidr_blocks  = var.admin_cidr_blocks
  instance_type      = var.instance_type
  common_tags        = local.common_tags
}

module "cloudtrail" {
  source = "./infra/modules/cloudtrail"

  name_prefix = local.name_prefix
  common_tags = local.common_tags
}
```

- [ ] **Step 5: Create root outputs**

Create `outputs.tf` with outputs for `vpc_id`, subnet IDs, app security group,
CloudTrail ARN, CloudTrail bucket, AWS Config recorder name, and VPC Flow Log ID.

- [ ] **Step 6: Create root example variables**

Create `terraform.tfvars.example` with:

```hcl
aws_region         = "ap-southeast-1"
project_name       = "cis-baseline"
environment        = "dev"
owner              = "security-team"
cost_center        = "security"
compliance_scope   = "cis-aws-foundations"
vpc_cidr           = "10.0.0.0/16"
enable_nat_gateway = true
admin_cidr_blocks  = []
instance_type      = "t3.micro"
```

---

### Task 2: Network Module Refactor

**Files:**
- Modify: `infra/modules/network/variables.tf`
- Modify: `infra/modules/network/locals.tf`
- Modify: `infra/modules/network/provider.tf`
- Modify: `infra/modules/network/vpc.tf`
- Modify: `infra/modules/network/vpc_b.tf`
- Modify: `infra/modules/network/peering.tf`
- Modify: `infra/modules/network/nacl.tf`
- Modify: `infra/modules/network/outputs.tf`
- Modify: `infra/modules/network/terraform.tfvars.example`
- Modify: `infra/modules/network/README.md`

- [ ] **Step 1: Replace module inputs**

Set `infra/modules/network/variables.tf` to use:

```hcl
variable "name_prefix" {
  description = "Global resource name prefix."
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block for the main VPC."
  type        = string
}

variable "az_count" {
  description = "Number of availability zones to use."
  type        = number
  default     = 2
}

variable "enable_nat_gateway" {
  description = "Create NAT gateways for private subnet egress."
  type        = bool
  default     = true
}

variable "common_tags" {
  description = "Common tags inherited from the root stack."
  type        = map(string)
}
```

- [ ] **Step 2: Replace module locals**

Set `infra/modules/network/locals.tf` to derive two AZs and subnet CIDRs:

```hcl
locals {
  az_names = slice(data.aws_availability_zones.available.names, 0, var.az_count)

  public_subnet_cidrs      = [for index in range(var.az_count) : cidrsubnet(var.vpc_cidr, 8, index)]
  private_app_subnet_cidrs = [for index in range(var.az_count) : cidrsubnet(var.vpc_cidr, 8, index + 10)]
  private_data_subnet_cidrs = [
    for index in range(var.az_count) : cidrsubnet(var.vpc_cidr, 8, index + 20)
  ]

  module_tags = merge(var.common_tags, {
    Component = "network"
  })
}
```

- [ ] **Step 3: Remove provider ownership from module**

Keep `terraform.required_providers` and data sources in `infra/modules/network/provider.tf`, but remove the `provider "aws"` block so the root provider owns region and default tags.

- [ ] **Step 4: Replace VPC and subnet resources**

Rewrite `infra/modules/network/vpc.tf` to create:

- `aws_vpc.main`
- `aws_internet_gateway.main`
- `aws_subnet.public`
- `aws_subnet.private_app`
- `aws_subnet.private_data`
- `aws_eip.nat`
- `aws_nat_gateway.main`
- route tables and associations for each tier

Use names such as `${var.name_prefix}-vpc-main`, `${var.name_prefix}-subnet-public-a`, and `${var.name_prefix}-rt-private-app-a`.

- [ ] **Step 5: Replace NACL rules with tier-specific defaults**

Rewrite `infra/modules/network/nacl.tf` to create one public NACL and one private NACL. Do not allow SSH, RDP, or SMB from `0.0.0.0/0`. Allow HTTP/HTTPS inbound to public subnets, ephemeral return traffic, and internal VPC traffic for private tiers.

- [ ] **Step 6: Add VPC Flow Logs**

Add resources:

```hcl
resource "aws_cloudwatch_log_group" "vpc_flow_logs" {
  name              = "/aws/vpc-flow-logs/${var.name_prefix}-vpc-main"
  retention_in_days = 365

  tags = merge(local.module_tags, {
    Name = "${var.name_prefix}-logs-vpc-flow"
  })
}

resource "aws_iam_role" "vpc_flow_logs" {
  name = "${var.name_prefix}-role-vpc-flow-logs"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "vpc-flow-logs.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_flow_log" "main" {
  iam_role_arn    = aws_iam_role.vpc_flow_logs.arn
  log_destination = aws_cloudwatch_log_group.vpc_flow_logs.arn
  traffic_type    = "ALL"
  vpc_id          = aws_vpc.main.id
}
```

Add the matching IAM role policy for CloudWatch Logs write permissions.

- [ ] **Step 7: Remove old two-VPC and peering resources**

Make `infra/modules/network/vpc_b.tf` and `infra/modules/network/peering.tf` empty except for comments stating that the shared-services VPC is intentionally not part of this baseline.

- [ ] **Step 8: Replace outputs**

Expose `vpc_id`, `vpc_cidr`, `public_subnet_ids`, `private_app_subnet_ids`,
`private_data_subnet_ids`, `nat_gateway_ids`, `vpc_flow_log_id`, and
`vpc_flow_log_group_name`.

---

### Task 3: Compute Module Hardening

**Files:**
- Modify: `infra/modules/compute/variables.tf`
- Modify: `infra/modules/compute/locals.tf`
- Modify: `infra/modules/compute/provider.tf`
- Modify: `infra/modules/compute/security_groups.tf`
- Modify: `infra/modules/compute/ec2.tf`
- Modify: `infra/modules/compute/outputs.tf`
- Modify: `infra/modules/compute/terraform.tfvars.example`
- Modify: `infra/modules/compute/README.md`

- [ ] **Step 1: Replace compute variables**

Use inputs `name_prefix`, `vpc_id`, `vpc_cidr`, `private_subnet_ids`,
`instance_type`, `admin_cidr_blocks`, and `common_tags`.

- [ ] **Step 2: Remove provider ownership from module**

Keep `terraform.required_providers`, remove the module-level `provider "aws"` block.

- [ ] **Step 3: Replace security group rules**

Create `aws_security_group.app` with:

- Ingress from `var.vpc_cidr` to port 80 for internal HTTP.
- Conditional SSH ingress only when `admin_cidr_blocks` is not empty.
- Egress to `0.0.0.0/0` and `::/0`.

Do not create RDP or SMB ingress rules.

- [ ] **Step 4: Add IAM instance role**

Create `aws_iam_role.app_instance`, `aws_iam_instance_profile.app`, and attach
`arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore` so private instances can
be managed through SSM instead of public SSH.

- [ ] **Step 5: Harden EC2 instances**

Update `aws_instance.app`:

```hcl
resource "aws_instance" "app" {
  count         = length(var.private_subnet_ids)
  ami           = data.aws_ami.amazon_linux_2023.id
  instance_type = var.instance_type
  subnet_id     = var.private_subnet_ids[count.index]

  vpc_security_group_ids      = [aws_security_group.app.id]
  associate_public_ip_address = false
  iam_instance_profile        = aws_iam_instance_profile.app.name
  monitoring                  = true

  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 1
    instance_metadata_tags      = "enabled"
  }

  root_block_device {
    volume_type           = "gp3"
    volume_size           = 20
    encrypted             = true
    delete_on_termination = true
  }

  tags = merge(local.module_tags, {
    Name = "${var.name_prefix}-ec2-app-${count.index + 1}"
    Tier = "app"
  })
}
```

- [ ] **Step 6: Replace outputs**

Expose app instance IDs, private IPs, security group ID, IAM role name, and
instance profile name. Remove public IP and SSH command outputs.

---

### Task 4: CloudTrail And Logging Module Refactor

**Files:**
- Modify: `infra/modules/cloudtrail/variables.tf`
- Modify: `infra/modules/cloudtrail/main.tf`
- Modify: `infra/modules/cloudtrail/s3.tf`
- Modify: `infra/modules/cloudtrail/kms.tf`
- Modify: `infra/modules/cloudtrail/cloudtrail.tf`
- Create: `infra/modules/cloudtrail/config.tf`
- Modify: `infra/modules/cloudtrail/outputs.tf`
- Modify: `infra/modules/cloudtrail/terraform.tfvars.example`
- Modify: `infra/modules/cloudtrail/README.md`

- [ ] **Step 1: Replace module variables**

Use `name_prefix`, `common_tags`, `cloudtrail_retention_days`,
`config_snapshot_delivery_frequency`, and booleans for S3 read/write data events.

- [ ] **Step 2: Remove provider ownership from module**

Keep `terraform.required_providers` and data sources in `main.tf`, remove
module-level `provider "aws"`.

- [ ] **Step 3: Normalize locals**

Create bucket names from `name_prefix`, account ID, and region:

```hcl
locals {
  cloudtrail_bucket_name = lower("${var.name_prefix}-cloudtrail-${data.aws_caller_identity.current.account_id}-${data.aws_region.current.name}")
  access_log_bucket_name = lower("${var.name_prefix}-s3-access-logs-${data.aws_caller_identity.current.account_id}-${data.aws_region.current.name}")

  module_tags = merge(var.common_tags, {
    Component = "logging"
  })
}
```

- [ ] **Step 4: Harden S3 buckets**

Create two buckets:

- `aws_s3_bucket.cloudtrail_logs`
- `aws_s3_bucket.access_logs`

For both buckets add versioning, ownership controls, public access block, and
server-side encryption. Enable server access logging on `cloudtrail_logs` with
target bucket `access_logs`.

- [ ] **Step 5: Update KMS policy**

Keep root account administration and CloudTrail permissions. Add AWS Config
service permissions when AWS Config writes encrypted snapshots to S3.

- [ ] **Step 6: Update CloudTrail**

Use:

```hcl
resource "aws_cloudtrail" "main" {
  name                          = "${var.name_prefix}-trail-main"
  s3_bucket_name                = aws_s3_bucket.cloudtrail_logs.id
  kms_key_id                    = aws_kms_key.cloudtrail.arn
  include_global_service_events = true
  is_multi_region_trail         = true
  enable_log_file_validation    = true
  enable_logging                = true

  event_selector {
    read_write_type           = "All"
    include_management_events = true

    data_resource {
      type   = "AWS::S3::Object"
      values = ["arn:${data.aws_partition.current.partition}:s3:::"]
    }
  }
}
```

- [ ] **Step 7: Add AWS Config**

Create:

- `aws_iam_role.config`
- `aws_iam_role_policy_attachment.config`
- `aws_config_configuration_recorder.main`
- `aws_config_delivery_channel.main`
- `aws_config_configuration_recorder_status.main`

Configure recording for all supported resources and global resources.

- [ ] **Step 8: Replace outputs**

Expose CloudTrail ARN, bucket names, KMS key ARN, AWS Config recorder name, and
AWS Config delivery channel name.

---

### Task 5: Documentation And Examples

**Files:**
- Modify: `infra/modules/network/README.md`
- Modify: `infra/modules/compute/README.md`
- Modify: `infra/modules/cloudtrail/README.md`
- Modify: `infra/modules/*/terraform.tfvars.example`

- [ ] **Step 1: Update module READMEs**

Each module README must state that the root stack is the supported entry point
and list the module inputs/outputs.

- [ ] **Step 2: Update module examples**

Keep module `terraform.tfvars.example` files only as local development examples.
Align values with root names: `cis-baseline`, `dev`, and private subnet usage.

---

### Task 6: Verification

**Files:**
- No planned file edits.

- [ ] **Step 1: Format Terraform**

Run:

```powershell
terraform fmt -recursive
```

Expected: command exits `0`; changed files are formatted.

- [ ] **Step 2: Validate root stack**

Run:

```powershell
terraform init -backend=false
terraform validate
```

Expected: `Success! The configuration is valid.`

- [ ] **Step 3: Static hardening checks**

Run:

```powershell
rg 'http_tokens\\s*=\\s*"optional"|encrypted\\s*=\\s*false|3389|445|cidr_ipv4\\s*=\\s*"0\\.0\\.0\\.0/0"' modules
```

Expected: no matches for vulnerable compute/network defaults. Matches in
documentation are acceptable only when they describe removed legacy behavior.

- [ ] **Step 4: Review final diff**

Run:

```powershell
git diff --stat
git diff -- modules providers.tf variables.tf locals.tf main.tf outputs.tf terraform.tfvars.example
```

Expected: diff contains only Terraform baseline refactor and matching docs.

---

## Self-Review

- Spec coverage: root stack, naming/tags, network, compute, CloudTrail/logging,
  data flow, validation, and verification are covered.
- Placeholder scan: no `TBD`, `TODO`, or open-ended implementation placeholders.
- Type consistency: root module arguments match planned module variables:
  `name_prefix`, `common_tags`, `vpc_id`, `private_subnet_ids`, `vpc_cidr`,
  `admin_cidr_blocks`, and `instance_type`.
