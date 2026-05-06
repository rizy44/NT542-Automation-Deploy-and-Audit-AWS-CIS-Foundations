# Security Auditing Lab - VPC & Compute Infrastructure

## Overview

This Terraform configuration builds an **intentional vulnerability lab** for practicing **CIS AWS Foundations Benchmark** compliance auditing. The infrastructure consists of two VPCs connected via VPC Peering, with a single vulnerable EC2 instance deployed in VPC A for testing security controls and audit tools.

## Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                    AWS Region: ap-southeast-1                   │
├────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────┐   ┌──────────────────┐   │
│  │     VPC A (Main Environment)     │   │  VPC B (Partner) │   │
│  │     10.0.0.0/16                  │   │  10.1.0.0/16     │   │
│  │                                  │   │                  │   │
│  │  ┌──────────────────────────┐    │   │  ┌────────────┐  │   │
│  │  │  Public Subnet (IGW)     │    │   │  │  Private   │  │   │
│  │  │  10.0.1.0/24             │    │   │  │  Subnet    │  │   │
│  │  │                          │    │   │  │  10.1.1.0  │  │   │
│  │  │  ┌────────────────────┐  │    │   │  └────────────┘  │   │
│  │  │  │  EC2 Instance      │  │    │   │                  │   │
│  │  │  │  t2.micro          │  │    │   │  (No instances)  │   │
│  │  │  │  (Vulnerable)      │  │    │   │                  │   │
│  │  │  └────────────────────┘  │    │   │                  │   │
│  │  └──────────────────────────┘    │   └──────────────────┘   │
│  │         Routes (IGW + Peering)   │   Routes (Peering only)  │
│  └──────────────────────────────────┘   ├──────────────────────┘
│                      ▲                    │
│                      │                    │
│                      └────────────────────┘
│                    VPC Peering Connection
│                    (Auto-Accept Enabled)
│
└────────────────────────────────────────────────────────────────┘
```

## Implemented Vulnerabilities

This lab implements **6 intentional misconfigurations** to practice CIS AWS Foundations Benchmark auditing:

### Vulnerability 1: Network ACL - Unrestricted SSH & RDP Access
- **Resource**: Network ACL on VPC A Public Subnet
- **Configuration**: Inbound rules ALLOW:
  - TCP port 22 (SSH) from 0.0.0.0/0
  - TCP port 3389 (RDP) from 0.0.0.0/0
  - Ephemeral ports (1024-65535) for return traffic
- **CIS Impact**: Violates CIS 3.1 - Unrestricted SSH access
- **Remediation**: Restrict to specific CIDR blocks or security groups
- **Terraform File**: `nacl.tf`

### Vulnerability 2: VPC A Default Security Group - Unchanged
- **Resource**: Default Security Group in VPC A
- **Configuration**: Left unchanged (default rules allow inbound from same SG)
- **CIS Impact**: Violates CIS 4.3 - Security groups should not allow unrestricted traffic
- **Remediation**: Apply restrictive rules or remove all inbound rules
- **Terraform File**: `security_groups.tf`
- **Note**: This is a data source reference to the unmodified default SG

### Vulnerability 3: Custom Security Group - Unrestricted SSH, RDP, SMB
- **Resource**: Custom Security Group for EC2 instance
- **Configuration**: Inbound rules ALLOW from 0.0.0.0/0 and ::/0:
  - TCP port 22 (SSH) - IPv4 and IPv6
  - TCP port 3389 (RDP) - IPv4 and IPv6
  - TCP port 445 (SMB) - IPv4 and IPv6
  - Outbound: Allow all traffic
- **CIS Impact**: Violates CIS 4.1-4.3 - Unrestricted management ports
- **Remediation**: Restrict to bastion host or VPN CIDR blocks
- **Terraform File**: `security_groups.tf`

### Vulnerability 4: EC2 Instance Metadata - IMDSv1 Enabled
- **Resource**: EC2 Instance metadata options
- **Configuration**:
  - `http_endpoint` = "enabled"
  - `http_tokens` = "optional" (VULNERABILITY)
  - `http_put_response_hop_limit` = 1
- **Impact**: Allows IMDSv1 access (can be exploited via SSRF attacks)
- **CIS Impact**: Violates CIS 4.7 - Should enforce IMDSv2 only (`http_tokens = "required"`)
- **Remediation**: Set `http_tokens = "required"` to enforce IMDSv2
- **Terraform File**: `ec2.tf`
- **Test Command**: `curl http://169.254.169.254/latest/meta-data/` from EC2 instance

### Vulnerability 5: EC2 Root EBS Volume - NOT Encrypted
- **Resource**: EC2 instance root block device
- **Configuration**: `encrypted = false` (explicit)
- **CIS Impact**: Violates CIS 2.2.1 - EBS volumes should be encrypted
- **Remediation**: Set `encrypted = true`
- **Terraform File**: `ec2.tf`
- **Note**: Account-level default EBS encryption is NOT enabled (configuration is explicit)
- **Verification**: Check AWS Console → EC2 → Instances → Storage → Root Volume → Encrypted field

### Vulnerability 6: VPC B Default Security Group - Unchanged
- **Resource**: Default Security Group in VPC B
- **Configuration**: Left unchanged (default rules allow inbound from same SG)
- **CIS Impact**: Same as Vulnerability 2
- **Remediation**: Apply restrictive rules
- **Terraform File**: `vpc_b.tf`
- **Note**: This is a data source reference to the unmodified default SG

---

## Project Structure

```
VPC_Compute/
├── provider.tf                    # AWS provider, version constraints, data sources
├── variables.tf                   # Input variables (region, CIDRs, instance type)
├── locals.tf                      # Common tags and computed values
├── vpc.tf                         # VPC A: VPC, IGW, public subnet, route tables
├── nacl.tf                        # Network ACL with vulnerable inbound rules
├── security_groups.tf             # Default SG (VPC A) and custom EC2 SG
├── vpc_b.tf                       # VPC B: VPC, private subnet, route tables, default SG
├── peering.tf                     # VPC Peering Connection (auto-accept)
├── ec2.tf                         # EC2 instance with vulnerable metadata + unencrypted EBS
├── outputs.tf                     # Stack outputs
├── terraform.tfvars.example       # Example configuration file
└── README.md                      # This file
```

## Prerequisites

- **AWS Account**: With appropriate IAM permissions (EC2, VPC, IAM)
- **Terraform**: Version 1.5.0 or higher
- **AWS CLI**: Optional, for manual verification
- **AWS Credentials**: Configured locally (AWS CLI profile or environment variables)

### Required IAM Permissions

Minimal permissions needed:
```
ec2:*
vpc:*
securitygroup:*
```

## Deployment Instructions

### 1. Clone or Navigate to the VPC_Compute Directory

```bash
cd /path/to/NT542-Automation-Deploy-and-Audit-AWS-CIS-Foundations/VPC_Compute
```

### 2. Create terraform.tfvars

Copy the example file and adjust as needed:

```bash
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` to customize:
- AWS region (default: `ap-southeast-1`)
- VPC CIDR blocks (defaults: VPC A `10.0.0.0/16`, VPC B `10.1.0.0/16`)
- Instance type (default: `t2.micro`)
- Environment name (default: `lab`)

### 3. Initialize Terraform

```bash
terraform init
```

This downloads the AWS provider and initializes the working directory.

### 4. Validate Configuration

```bash
terraform fmt -check    # Check formatting
terraform validate       # Validate syntax and references
```

### 5. Preview Infrastructure

```bash
terraform plan
```

Review the proposed changes. Verify:
- Two VPCs are created with correct CIDRs
- EC2 instance is created with `http_tokens = "optional"`
- Root volume is NOT encrypted
- NACL and SG rules allow SSH/RDP from 0.0.0.0/0

### 6. Apply Configuration

```bash
terraform apply
```

Type `yes` when prompted to create the infrastructure.

### 7. Capture Outputs

```bash
terraform output
```

Important outputs:
- `ec2_instance_public_ip`: Public IP of the vulnerable instance
- `vpc_peering_connection_id`: Peering connection ID
- `vulnerabilities_summary`: Summary of all implemented vulnerabilities

## Testing & Verification

### Test 1: Verify NACL Rules

```bash
# List NACL rules
aws ec2 describe-network-acls --query 'NetworkAcls[?Tags[?Key==`Name`]].NetworkAclEntries' --output table
```

Expected: Inbound rules for ports 22 and 3389 from 0.0.0.0/0.

### Test 2: Verify Security Group Rules

```bash
# Get EC2 security group ID
SG_ID=$(terraform output -raw ec2_security_group_id)

# List rules
aws ec2 describe-security-groups --group-ids $SG_ID --output table
```

Expected: Inbound rules for ports 22, 3389, 445 from 0.0.0.0/0 and ::/0.

### Test 3: Verify EC2 Metadata Configuration

```bash
# SSH to EC2 instance
INSTANCE_IP=$(terraform output -raw ec2_instance_public_ip)
ssh -i /path/to/key.pem ec2-user@$INSTANCE_IP

# On the instance, test IMDSv1 access (should succeed)
curl http://169.254.169.254/latest/meta-data/

# On the instance, test IMDSv2 access (should also succeed with -H headers)
TOKEN=$(curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/
```

### Test 4: Verify EBS Encryption Status

```bash
# List EC2 root volumes
aws ec2 describe-volumes --query 'Volumes[?Tags[?Key==`Name`]].{VolumeId:VolumeId,Encrypted:Encrypted}' --output table
```

Expected: `Encrypted` field should be `false`.

### Test 5: Verify VPC Peering

```bash
# Check peering status
aws ec2 describe-vpc-peering-connections --query 'VpcPeeringConnections[*].{Id:VpcPeeringConnectionId,Status:Status}' --output table
```

Expected: Status should be `active`.

### Test 6: Run CIS Audit Checks

If running with the `Ver_Cloudtrail` verification suite:

```bash
cd ../Ver_Cloudtrail
python benchmark_checker.py
```

Expected: Checks should detect all 6 vulnerabilities.

## Cleanup Instructions

To remove all infrastructure:

```bash
cd VPC_Compute

# Preview deletion
terraform plan -destroy

# Delete all resources
terraform destroy
```

Type `yes` when prompted to confirm deletion.

**Warning**: This will delete:
- EC2 instances
- VPCs, subnets, route tables
- Internet gateways
- VPC peering connections
- Security groups
- Network ACLs

## Cost Considerations

- **EC2 Instance** (t2.micro): AWS Free Tier eligible (if within 12-month trial)
- **Data Transfer**: Minimal (only peering traffic)
- **Storage**: 20 GB root volume (gp3, ~$1.30/month)
- **Estimated Monthly Cost**: $0-2 USD (within Free Tier) or ~$2-5 if outside Free Tier

To minimize costs:
- Use `terraform destroy` when not actively testing
- Run during AWS Free Tier eligibility period

## Terraform Conventions

This project follows the conventions established in the `Cloudtrail/` module:

- **File Organization**: Service-specific files (vpc.tf, ec2.tf, etc.)
- **Naming**: `.this` suffix for primary resources, descriptive names for secondary
- **Tagging**: `common_tags` local with Environment, Project, ManagedBy tags
- **Data Sources**: Dynamic values via `aws_caller_identity`, `aws_region`, `aws_partition`
- **Variables**: Documented with descriptions, types, and defaults
- **Outputs**: Comprehensive outputs for infrastructure details and verification

## Troubleshooting

### Issue: Terraform init fails with provider error

**Solution**:
```bash
# Ensure AWS credentials are configured
aws sts get-caller-identity

# Reinitialize Terraform
rm -rf .terraform
terraform init
```

### Issue: EC2 instance fails to launch

**Solution**:
```bash
# Verify AMI availability in region
aws ec2 describe-images --owners amazon --filters "Name=name,Values=al2023-ami-*" --query 'Images[0].ImageId'

# Verify instance type availability
aws ec2 describe-instance-types --instance-types t2.micro --query 'InstanceTypes[0].SupportedArchitectures'
```

### Issue: VPC Peering connection shows "pcx-xxxxxxxx" but not active

**Solution**:
```bash
# Wait 30 seconds and check status
sleep 30
terraform output vpc_peering_connection_status

# If still pending, manually accept in AWS Console or re-apply
terraform apply -target=aws_vpc_peering_connection_accepter.main
```

### Issue: SSH to EC2 fails

**Causes**:
1. Security group rules not applied yet (wait 1-2 minutes)
2. Key pair not specified or incorrect path
3. EC2 instance still initializing (wait 1-2 minutes)

**Solution**:
```bash
# Verify security group inbound rule
aws ec2 authorize-security-group-ingress --group-id <sg-id> --protocol tcp --port 22 --cidr 0.0.0.0/0

# Check EC2 instance status
aws ec2 describe-instance-status --instance-ids $(terraform output -raw ec2_instance_id)
```

## References

- **CIS AWS Foundations Benchmark**: https://www.cisecurity.org/benchmark/amazon-web-services
- **AWS VPC Documentation**: https://docs.aws.amazon.com/vpc/
- **AWS EC2 Documentation**: https://docs.aws.amazon.com/ec2/
- **Terraform AWS Provider**: https://registry.terraform.io/providers/hashicorp/aws/latest/docs

## License

This lab infrastructure is provided for educational purposes as part of the NT542 AWS Automation project.

## Support

For questions or issues with the lab:
1. Check the Troubleshooting section above
2. Review the Terraform outputs: `terraform output`
3. Check AWS CloudTrail logs for failed API calls
4. Verify AWS credentials and IAM permissions

---

**Last Updated**: May 4, 2026  
**Terraform Version**: >= 1.5.0  
**AWS Provider**: ~> 5.0
