# CIS Monitoring Terraform Module

This module provisions CIS AWS Foundations Benchmark Section 5 monitoring controls as an independent deployment unit.

## Scope

- Creates CloudWatch metric filters and alarms for CIS 5.1 to 5.15.
- Creates one SNS topic and optional email subscription reused by all alarms.
- Enables Security Hub for CIS 5.16.
- Does not create or manage CloudTrail trails.

## Prerequisites

1. CloudTrail must already be enabled in all required regions.
2. CloudTrail must already send management events to CloudWatch Logs.
3. Provide the target CloudTrail log group name via cloudtrail_log_group_name.
4. This module creates the CloudWatch log group named by cloudtrail_log_group_name.
5. Enable Security Hub explicitly if you want Terraform to manage CIS 5.16 in a new account.

## Controls Implemented

- 5.1 Unauthorized API calls
- 5.2 Console sign-in without MFA
- 5.3 Root account usage
- 5.4 IAM policy changes
- 5.5 CloudTrail configuration changes
- 5.6 Console authentication failures
- 5.7 Disabling/scheduled deletion of CMKs
- 5.8 S3 bucket policy changes
- 5.9 AWS Config changes
- 5.10 Security group changes
- 5.11 NACL changes
- 5.12 Network gateway changes
- 5.13 Route table changes
- 5.14 VPC changes
- 5.15 AWS Organizations changes
- 5.16 Security Hub enabled

## Quick Start

```bash
terraform init
terraform fmt -recursive
terraform validate
terraform plan -var-file="terraform.tfvars"
terraform apply -var-file="terraform.tfvars"
```

## Running the Benchmark Checker

The repository contains a runtime checker that validates the monitoring controls created by this module. From the repository root run:

```bash
cd scripts/Ver_Monitor
pip install -r requirements.txt
python benchmark_checker.py --log-group /aws/cloudtrail/<your-log-group> --profile <aws-profile>
```

Use `--controls` to restrict checks (e.g. `5.1,5.2,5.16`) and `--regions` to limit regions.

## Standard CIS CLI Remediation Template

```bash
aws logs put-metric-filter --log-group-name <trail-log-group-name> --filter-name <metric-name> --metric-transformations metricName=<metric-name>,metricNamespace='CISBenchmark',metricValue=1 --filter-pattern '<pattern>'
aws sns create-topic --name <sns-topic-name>
aws sns subscribe --topic-arn <sns-topic-arn> --protocol <sns-protocol> --notification-endpoint <sns-subscription-endpoints>
aws cloudwatch put-metric-alarm --alarm-name <alarm-name> --metric-name <metric-name> --statistic Sum --period 300 --threshold 1 --comparison-operator GreaterThanOrEqualToThreshold --evaluation-periods 1 --namespace 'CISBenchmark' --alarm-actions <sns-topic-arn>
```
