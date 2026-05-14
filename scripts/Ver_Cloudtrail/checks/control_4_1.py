"""
CIS 4.1: Ensure CloudTrail is enabled in all regions.
"""
import logging

from scripts.Ver_Cloudtrail.config import CIS_CONTROLS
from scripts.Ver_Cloudtrail.checks.common import discover_trails, get_trail_status
from scripts.Ver_Cloudtrail.utils import create_result, error_handler

logger = logging.getLogger(__name__)


@error_handler
def check_control_4_1(profile_name=None, regions=None):
    control_id = "4.1"
    control = CIS_CONTROLS[control_id]

    trails, discovery_errors = discover_trails(profile_name=profile_name, regions=regions)
    if not trails:
        return create_result(
            control_id,
            control["title"],
            "FAIL",
            control["severity"],
            details={"reason": "No CloudTrail trails configured", "discovery_errors": discovery_errors},
            remediation="Create a multi-region CloudTrail trail with logging and global service events enabled",
        )

    compliant_trails = []
    all_details = []

    for trail in trails:
        try:
            status = get_trail_status(trail, profile_name=profile_name)
            is_logging = status.get("IsLogging", False)
        except Exception as exc:
            logger.warning("Could not get status for trail %s: %s", trail.get("Name"), exc)
            is_logging = False

        trail_info = {
            "trail_name": trail.get("Name"),
            "arn": trail.get("TrailARN"),
            "home_region": trail.get("HomeRegion"),
            "is_multi_region": trail.get("IsMultiRegionTrail", False),
            "include_global_service_events": trail.get("IncludeGlobalServiceEvents", False),
            "is_logging": is_logging,
        }
        all_details.append(trail_info)

        if (
            trail.get("IsMultiRegionTrail", False)
            and trail.get("IncludeGlobalServiceEvents", False)
            and is_logging
        ):
            compliant_trails.append(trail.get("Name"))

    status = "PASS" if compliant_trails else "FAIL"
    return create_result(
        control_id,
        control["title"],
        status,
        control["severity"],
        details={
            "compliant_multi_region_trails": compliant_trails,
            "all_trails": all_details,
            "discovery_errors": discovery_errors,
        },
        resource_id=",".join(compliant_trails) if compliant_trails else None,
        remediation="Enable a multi-region CloudTrail trail with logging and global service events" if status == "FAIL" else None,
    )
