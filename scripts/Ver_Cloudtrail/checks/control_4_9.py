"""
CIS 4.9: Ensure object-level logging for read events is enabled for S3 buckets.
"""
import logging

from scripts.Ver_Cloudtrail.config import CIS_CONTROLS, get_client
from scripts.Ver_Cloudtrail.checks.common import discover_trails, event_selectors_have_s3_logging
from scripts.Ver_Cloudtrail.utils import create_result, error_handler

logger = logging.getLogger(__name__)


@error_handler
def check_control_4_9(profile_name=None, regions=None):
    control_id = "4.9"
    control = CIS_CONTROLS[control_id]
    trails, discovery_errors = discover_trails(profile_name=profile_name, regions=regions)
    if not trails:
        return create_result(
            control_id,
            control["title"],
            "FAIL",
            control["severity"],
            details={"reason": "No CloudTrail trails found", "discovery_errors": discovery_errors},
            remediation="Configure CloudTrail S3 data events for read activity",
        )

    enabled = []
    disabled = []
    all_details = []

    for trail in trails:
        trail_name = trail.get("Name")
        try:
            region = trail.get("HomeRegion") or (trail.get("DiscoveredRegions") or [None])[0]
            client = get_client("cloudtrail", region_name=region, profile_name=profile_name)
            response = client.get_event_selectors(TrailName=trail.get("TrailARN") or trail_name)
            has_logging = event_selectors_have_s3_logging(response, "read")
            all_details.append(
                {
                    "trail_name": trail_name,
                    "trail_arn": trail.get("TrailARN"),
                    "has_s3_read_logging": has_logging,
                    "event_selectors": response.get("EventSelectors", []),
                    "advanced_event_selectors": response.get("AdvancedEventSelectors", []),
                }
            )
            if has_logging:
                enabled.append(trail_name)
            else:
                disabled.append(trail_name)
        except Exception as exc:
            logger.warning("Could not inspect event selectors for %s: %s", trail_name, exc)
            all_details.append({"trail_name": trail_name, "error": str(exc)})
            disabled.append(trail_name)

    status = "PASS" if enabled else "FAIL"
    return create_result(
        control_id,
        control["title"],
        status,
        control["severity"],
        details={
            "trails_with_read_logging": enabled,
            "trails_without_read_logging": disabled,
            "all_trails": all_details,
            "discovery_errors": discovery_errors,
        },
        resource_id=",".join(enabled) if enabled else None,
        remediation="Enable CloudTrail S3 object-level data event logging for read events" if status == "FAIL" else None,
    )
