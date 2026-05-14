"""
CIS 4.4: Ensure server access logging is enabled on the CloudTrail S3 bucket.
"""
import logging

from scripts.Ver_Cloudtrail.config import CIS_CONTROLS, get_client
from scripts.Ver_Cloudtrail.checks.common import discover_trails
from scripts.Ver_Cloudtrail.utils import create_result, error_handler

logger = logging.getLogger(__name__)


@error_handler
def check_control_4_4(profile_name=None, regions=None):
    control_id = "4.4"
    control = CIS_CONTROLS[control_id]
    trails, discovery_errors = discover_trails(profile_name=profile_name, regions=regions)
    if not trails:
        return create_result(
            control_id,
            control["title"],
            "FAIL",
            control["severity"],
            details={"reason": "No CloudTrail trails found", "discovery_errors": discovery_errors},
            remediation="Enable CloudTrail and enable server access logging on its S3 log bucket",
        )

    s3_client = get_client("s3", profile_name=profile_name)
    buckets = sorted({trail.get("S3BucketName") for trail in trails if trail.get("S3BucketName")})
    enabled = []
    disabled = []
    all_details = []

    for bucket in buckets:
        try:
            logging_config = s3_client.get_bucket_logging(Bucket=bucket)
            logging_rules = logging_config.get("LoggingEnabled")
            bucket_info = {
                "bucket_name": bucket,
                "logging_enabled": bool(logging_rules),
                "target_bucket": logging_rules.get("TargetBucket") if logging_rules else None,
                "target_prefix": logging_rules.get("TargetPrefix") if logging_rules else None,
            }
            all_details.append(bucket_info)
            if logging_rules:
                enabled.append(bucket)
            else:
                disabled.append(bucket)
        except Exception as exc:
            logger.warning("Could not check access logging for bucket %s: %s", bucket, exc)
            all_details.append({"bucket_name": bucket, "logging_enabled": False, "error": str(exc)})
            disabled.append(bucket)

    status = "PASS" if buckets and not disabled else "FAIL"
    return create_result(
        control_id,
        control["title"],
        status,
        control["severity"],
        details={
            "logging_enabled_buckets": enabled,
            "logging_disabled_buckets": disabled,
            "all_buckets": all_details,
            "discovery_errors": discovery_errors,
        },
        resource_id=",".join(enabled) if enabled else None,
        remediation="Enable S3 server access logging on every CloudTrail log bucket" if status == "FAIL" else None,
    )
