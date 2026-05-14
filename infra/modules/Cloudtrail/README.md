# CloudTrail Module

This module is part of the root Terraform stack under `infra/`. Use `infra/` as
the supported entry point; running this module directly is only for local module
development.

## Resources

- Multi-region CloudTrail with global service events, log file validation, KMS encryption, and S3 object data events.
- CloudTrail log bucket with versioning, public access blocks, ownership controls, KMS encryption, lifecycle retention, and access logging.
- Dedicated S3 access log bucket for CloudTrail bucket access logs.
- AWS Config delivery bucket with versioning, public access blocks, ownership controls, and AES256 encryption.
- Customer managed KMS key and alias for CloudTrail logs.
- AWS Config recorder, delivery channel, service role, and managed policy attachment in the active provider region.

## Inputs

| Name | Type | Default | Description |
| --- | --- | --- | --- |
| `name_prefix` | `string` | n/a | Prefix used for logging resource names. |
| `common_tags` | `map(string)` | n/a | Common tags applied to all logging resources. |
| `cloudtrail_retention_days` | `number` | `365` | Number of days to retain CloudTrail logs in S3. |
| `config_snapshot_delivery_frequency` | `string` | `"TwentyFour_Hours"` | AWS Config snapshot delivery frequency. |
| `enable_s3_data_event_read_logging` | `bool` | `true` | Whether CloudTrail records S3 object read data events. |
| `enable_s3_data_event_write_logging` | `bool` | `true` | Whether CloudTrail records S3 object write data events. |

## Outputs

| Name | Description |
| --- | --- |
| `cloudtrail_arn` | ARN of the CloudTrail trail. |
| `cloudtrail_home_region` | Home region of the CloudTrail trail. |
| `cloudtrail_log_bucket_name` | S3 bucket name storing CloudTrail logs. |
| `cloudtrail_access_log_bucket_name` | S3 bucket name storing access logs for the CloudTrail log bucket. |
| `cloudtrail_kms_key_arn` | KMS key ARN used by CloudTrail. |
| `config_recorder_name` | Name of the AWS Config configuration recorder. |
| `config_delivery_channel_name` | Name of the AWS Config delivery channel. |
| `config_log_bucket_name` | S3 bucket name storing AWS Config delivery snapshots. |

## Root Usage

The root stack passes the shared name prefix and tags. Optional settings use module defaults unless the root stack sets them.

```hcl
module "cloudtrail" {
  source = "./modules/Cloudtrail"

  name_prefix = local.name_prefix
  common_tags = local.common_tags
}
```

## Regional Limitation

AWS Config is regional. This module enables AWS Config only in the active AWS
provider region. Full CIS 4.3 coverage across every enabled AWS region requires
instantiating AWS Config with provider aliases per region or splitting it into a
dedicated multi-region Config module.
