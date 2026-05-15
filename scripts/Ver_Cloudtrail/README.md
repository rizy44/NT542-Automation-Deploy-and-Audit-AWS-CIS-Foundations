# CIS AWS Foundations Benchmark v6 Logging Checker

Python tool for read-only assessment of CIS AWS Foundations Benchmark v6.0.0
Logging controls 4.1 through 4.9.

## Scope

- **4.1**: Ensure CloudTrail is enabled in all regions
- **4.2**: Ensure CloudTrail log file validation is enabled
- **4.3**: Ensure AWS Config is enabled in all regions
- **4.4**: Ensure server access logging is enabled on the CloudTrail S3 bucket
- **4.5**: Ensure CloudTrail logs are encrypted at rest using KMS CMKs
- **4.6**: Ensure rotation for customer-created symmetric CMKs is enabled
- **4.7**: Ensure VPC flow logging is enabled in all VPCs
- **4.8**: Ensure object-level logging for write events is enabled for S3 buckets
- **4.9**: Ensure object-level logging for read events is enabled for S3 buckets

## Installation

Prerequisites:

- Python 3.10 or higher
- AWS credentials configured through environment variables, AWS config files, or an IAM role

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run every CIS v6 logging control:

```bash
python benchmark_checker.py
```

Run selected controls:

```bash
python benchmark_checker.py --controls 4.1,4.2,4.3
```

Use a profile, selected regions, verbose logs, and JSON output:

```bash
python benchmark_checker.py \
  --profile prod \
  --regions us-east-1,us-west-2 \
  --output compliance-report.json \
  -v
```

## Output

The tool prints a console summary and the full JSON report. When `--output` is
provided, it also writes the JSON report to that path.

Status values:

- `PASS`: the checked configuration meets the control
- `FAIL`: the checked configuration does not meet the control
- `UNKNOWN`: the check could not be completed because of an API or permission issue

## Required Read-Only AWS Permissions

- CloudTrail: `DescribeTrails`, `GetTrailStatus`, `GetEventSelectors`
- AWS Config: `DescribeConfigurationRecorders`, `DescribeConfigurationRecorderStatus`, `DescribeDeliveryChannels`
- KMS: `ListKeys`, `DescribeKey`, `GetKeyRotationStatus`
- S3: `GetBucketLogging`
- EC2: `DescribeRegions`, `DescribeVpcs`, `DescribeFlowLogs`
- STS: `GetCallerIdentity`

## Architecture

```text
Ver_Cloudtrail/
  benchmark_checker.py
  config.py
  utils.py
  requirements.txt
  checks/
    common.py
    control_4_1.py
    ...
    control_4_9.py
  tests/
    test_cis_v6_controls.py
```
