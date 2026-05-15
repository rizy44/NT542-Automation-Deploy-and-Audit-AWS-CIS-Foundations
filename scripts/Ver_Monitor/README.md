# CIS AWS Monitoring Benchmark Checker

This tool checks CIS AWS Foundations Monitoring controls 5.1 through 5.16.

## Scope

- 5.1 to 5.15: verifies each control has both a CloudWatch metric filter and an alarm.
- 5.16: verifies Security Hub is enabled in target regions.

## Prerequisites

- Python 3.10+
- AWS credentials with read-only permissions for CloudWatch Logs, CloudWatch, Security Hub, EC2, and STS
- Existing CloudTrail log group in CloudWatch Logs

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Run all controls:

```bash
python benchmark_checker.py --log-group /aws/cloudtrail/main-cloudtrail
```

Run specific controls:

```bash
python benchmark_checker.py --controls 5.1,5.2,5.16 --log-group /aws/cloudtrail/main-cloudtrail
```

Run with profile, regions, output:

```bash
python benchmark_checker.py --profile prod --regions ap-southeast-1,us-east-1 --output monitor-report.json --log-group /aws/cloudtrail/main-cloudtrail
```

## Output

- Console summary with pass/fail counts.
- Full JSON report with details per control.
- Process exits with code 1 if any control fails.

## Notes

- 5.1 to 5.15 use the standard CIS model: metric filter plus alarm in namespace CISBenchmark.
- Use one SNS topic and reuse it for all alarms.
