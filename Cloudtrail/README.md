# CloudTrail Terraform Skeleton
## Files

- `main.tf`: Terraform + AWS provider + data sources + common locals.
- `variables.tf`: Bien dau vao cho region, trail, logging options.
- `s3.tf`: S3 bucket luu log CloudTrail va policy cho CloudTrail ghi log.
- `kms.tf`: KMS key va alias de ma hoa log.
- `cloudtrail.tf`: Tai nguyen CloudTrail chinh.
- `outputs.tf`: Output de tham chieu stack sau.
- `terraform.tfvars.example`: Mau gia tri de copy va chinh sua.

## Quick Start

```bash
terraform init
terraform fmt -recursive
terraform validate
terraform plan
```
