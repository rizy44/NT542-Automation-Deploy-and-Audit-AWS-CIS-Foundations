# CIS AWS CloudTrail Benchmark Checker

An automated Python-based security assessment tool for evaluating AWS configurations against CIS AWS Foundations Benchmark controls, focusing on CloudTrail and related services.

## Overview

This tool validates 9 CIS controls related to AWS CloudTrail, AWS Config, KMS, S3, and VPC Flow Logs. It performs read-only checks via AWS APIs and produces structured JSON compliance reports suitable for audit and compliance tracking.

### Scope

- **Control 3.1**: Ensure CloudTrail is enabled in all regions
- **Control 3.2**: Ensure log file validation is enabled
- **Control 3.3**: Ensure S3 bucket access logging is enabled
- **Control 3.4**: Ensure CloudTrail logs are encrypted with KMS CMK
- **Control 3.5**: Ensure KMS key rotation is enabled
- **Control 3.6**: Ensure AWS Config is enabled in all regions
- **Control 3.7**: Ensure VPC Flow Logs are enabled
- **Control 3.8**: Ensure S3 object-level logging for WRITE events
- **Control 3.9**: Ensure S3 object-level logging for READ events

## Installation

### Prerequisites
- Python 3.10 or higher
- AWS Account with appropriate permissions
- AWS credentials configured (via `~/.aws/credentials`, `~/.aws/config`, or environment variables)

### Setup

1. Clone or download this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

### Required AWS Permissions

The script requires read-only permissions for:
- CloudTrail: `cloudtrail:DescribeTrails`, `cloudtrail:GetTrailStatus`, `cloudtrail:GetEventSelectors`
- AWS Config: `config:DescribeConfigurationRecorders`, `config:DescribeConfigurationRecorderStatus`, `config:DescribeDeliveryChannels`
- KMS: `kms:DescribeKey`, `kms:GetKeyRotationStatus`
- S3: `s3:GetBucketLogging`
- EC2: `ec2:DescribeRegions`, `ec2:DescribeVpcs`, `ec2:DescribeFlowLogs`
- STS: `sts:GetCallerIdentity`

## Usage

### Basic Usage

Run all checks:
```bash
python benchmark_checker.py
```

### Run All Checks with Verbose Output

```bash
python benchmark_checker.py -v
```

### Run Specific Controls

```bash
python benchmark_checker.py --controls 3.1,3.2,3.3
```

### Save Report to File

```bash
python benchmark_checker.py --output report.json
```

### Use Specific AWS Profile

```bash
python benchmark_checker.py --profile production
```

### Check Specific Regions

```bash
python benchmark_checker.py --regions us-east-1,eu-west-1
```

### Combined Example

```bash
python benchmark_checker.py \
  --profile prod \
  --controls 3.1,3.2,3.4,3.5 \
  --regions us-east-1,us-west-2 \
  --output prod-compliance-report.json \
  -v
```

## Output Format

### Console Summary

```
============================================================
CIS AWS CloudTrail Benchmark - Results Summary
============================================================
Account ID: 123456789012
Regions Checked: ap-southeast-1, us-east-1
Execution Date: 2026-04-29T10:30:00Z
------------------------------------------------------------
Total Controls: 9
✓ Passed: 7
✗ Failed: 1
? Unknown: 1
Compliance: 77.78%
============================================================

⚠ Failed Controls:
  - CIS-3.7: Ensure VPC Flow Logs are enabled
    Remediation: Enable VPC Flow Logs for all VPCs
```

### JSON Report

```json
{
  "benchmark_name": "CIS AWS Foundations Benchmark - CloudTrail",
  "execution_date": "2026-04-29T10:30:00Z",
  "aws_account_id": "123456789012",
  "regions_checked": ["ap-southeast-1"],
  "summary": {
    "total_controls": 9,
    "passed": 7,
    "failed": 1,
    "unknown": 1,
    "compliance_percentage": 77.78
  },
  "results": [
    {
      "control_id": "CIS-3.1",
      "title": "Ensure CloudTrail is enabled in all regions",
      "status": "PASS",
      "severity": "CRITICAL",
      "resource_id": "multi-region-trail",
      "details": {
        "multi_region_trails": ["multi-region-trail"],
        "all_trails": [...]
      },
      "remediation": null,
      "timestamp": "2026-04-29T10:30:00Z"
    },
    ...
  ]
}
```

## Result Status Codes

| Status | Meaning | Action |
|--------|---------|--------|
| `PASS` | Configuration complies with CIS control | No action required |
| `FAIL` | Configuration does not comply with CIS control | Review remediation and take corrective action |
| `UNKNOWN` | Unable to verify due to permission error or API failure | Check AWS credentials and IAM permissions |

## Severity Levels

- **CRITICAL**: Control failure poses highest security risk
- **HIGH**: Control failure poses significant security risk
- **MEDIUM**: Control failure poses moderate security risk
- **LOW**: Control failure poses low security risk

## Architecture

```
Ver_Cloudtrail/
├── benchmark_checker.py    # Main entry point
├── config.py               # AWS client configuration
├── utils.py                # Output formatting and helpers
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── checks/                # Individual control implementations
    ├── __init__.py
    ├── control_3_1.py     # CloudTrail enabled
    ├── control_3_2.py     # Log file validation
    ├── control_3_3.py     # S3 access logging
    ├── control_3_4.py     # KMS encryption
    ├── control_3_5.py     # KMS key rotation
    ├── control_3_6.py     # AWS Config enabled
    ├── control_3_7.py     # VPC Flow Logs
    ├── control_3_8.py     # S3 object WRITE logging
    └── control_3_9.py     # S3 object READ logging
```

## Troubleshooting

### "Could not retrieve AWS account ID"
- Verify AWS credentials are properly configured
- Check that you have permission to call `sts:GetCallerIdentity`

### "AccessDenied" or "UnauthorizedOperation"
- Verify IAM role/user has required permissions
- Check policy configuration

### "No CloudTrail trails found"
- Ensure CloudTrail is enabled in your AWS account
- Verify you have permission to access CloudTrail in the target account/region

### Timeout or Connection Errors
- Check network connectivity to AWS APIs
- Verify you're not behind a restrictive proxy

## AWS CLI Integration

Export results for analysis:

```bash
# Generate report
python benchmark_checker.py --output compliance.json

# Extract failed controls using jq
jq '.results[] | select(.status == "FAIL")' compliance.json

# Get summary statistics
jq '.summary' compliance.json

# List all failed resource IDs
jq '.results[] | select(.status == "FAIL") | .resource_id' compliance.json
```

## CI/CD Integration

### GitHub Actions Example

```yaml
- name: Run CIS Benchmark
  env:
    AWS_PROFILE: default
  run: |
    pip install -r requirements.txt
    python benchmark_checker.py --output report.json
    
- name: Check Compliance
  run: |
    FAILED=$(jq '.summary.failed' report.json)
    if [ $FAILED -gt 0 ]; then
      echo "Compliance check failed"
      exit 1
    fi
```

## Performance

- Typical execution time: 2-5 minutes depending on number of regions and resources
- Regional checks are sequential to manage API rate limits
- Use `--regions` flag to reduce scope and improve speed

## Security Considerations

- Script performs read-only operations only
- No resource modifications or deletions
- Credentials handled securely by boto3
- Output may contain sensitive information; protect JSON reports appropriately

## Limitations

- Single AWS account scope (no cross-account checks)
- Manual controls (3.1, 3.3) converted to automated API-based checks
- Depends on CloudTrail, Config, and VPC Flow Logs features being available in target regions

## Contributing

To add new CIS controls:

1. Create new file in `checks/` folder following naming convention: `control_3_X.py`
2. Implement check function with proper error handling
3. Add control to `CIS_CONTROLS` dictionary in `config.py`
4. Import and map to control function in `benchmark_checker.py`

## License

This tool is provided as-is for security compliance assessment.

## References

- [CIS AWS Foundations Benchmark](https://www.cisecurity.org/cis-benchmarks)
- [AWS CloudTrail Documentation](https://docs.aws.amazon.com/cloudtrail/)
- [boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review AWS IAM permissions
3. Verify AWS credentials and region configuration
4. Check script logs with `-v` flag for detailed output

---

**Last Updated**: 2026-04-29
