"""
CIS 4.2: Ensure CloudTrail log file validation is enabled.
"""
from scripts.Ver_Cloudtrail.config import CIS_CONTROLS
from scripts.Ver_Cloudtrail.checks.common import discover_trails
from scripts.Ver_Cloudtrail.utils import create_result, error_handler


@error_handler
def check_control_4_2(profile_name=None, regions=None):
    control_id = "4.2"
    control = CIS_CONTROLS[control_id]
    trails, discovery_errors = discover_trails(profile_name=profile_name, regions=regions)

    if not trails:
        return create_result(
            control_id,
            control["title"],
            "FAIL",
            control["severity"],
            details={"reason": "No CloudTrail trails found", "discovery_errors": discovery_errors},
            remediation="Enable CloudTrail log file validation",
        )

    valid = [trail.get("Name") for trail in trails if trail.get("LogFileValidationEnabled", False)]
    invalid = [trail.get("Name") for trail in trails if not trail.get("LogFileValidationEnabled", False)]
    status = "PASS" if not invalid else "FAIL"

    return create_result(
        control_id,
        control["title"],
        status,
        control["severity"],
        details={
            "validated_trails": valid,
            "unvalidated_trails": invalid,
            "all_trails": [
                {
                    "trail_name": trail.get("Name"),
                    "arn": trail.get("TrailARN"),
                    "log_file_validation_enabled": trail.get("LogFileValidationEnabled", False),
                }
                for trail in trails
            ],
            "discovery_errors": discovery_errors,
        },
        resource_id=",".join(valid) if valid else None,
        remediation="Enable log file validation for all CloudTrail trails" if status == "FAIL" else None,
    )
