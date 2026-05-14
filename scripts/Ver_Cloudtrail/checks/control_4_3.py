"""
CIS 4.3: Ensure AWS Config is enabled in all regions.
"""
import logging

from scripts.Ver_Cloudtrail.config import CIS_CONTROLS, get_all_regions, get_client
from scripts.Ver_Cloudtrail.utils import create_result, error_handler

logger = logging.getLogger(__name__)


@error_handler
def check_control_4_3(profile_name=None, regions=None):
    control_id = "4.3"
    control = CIS_CONTROLS[control_id]
    if not regions:
        regions = get_all_regions(profile_name=profile_name)

    all_details = []
    compliant_regions = []
    noncompliant_regions = []
    global_resource_regions = []

    for region in regions:
        try:
            client = get_client("config", region_name=region, profile_name=profile_name)
            recorders = client.describe_configuration_recorders().get("ConfigurationRecorders", [])
            delivery_channels = client.describe_delivery_channels().get("DeliveryChannels", [])

            if not recorders:
                all_details.append({"region": region, "config_enabled": False, "reason": "No configuration recorder"})
                noncompliant_regions.append(region)
                continue

            recorder = recorders[0]
            recorder_name = recorder.get("name")
            status_response = client.describe_configuration_recorder_status(
                ConfigurationRecorderNames=[recorder_name]
            )
            recorder_status = status_response.get("ConfigurationRecordersStatus", [{}])[0]
            recording_group = recorder.get("recordingGroup", {})

            recording = recorder_status.get("recording", False)
            last_status = recorder_status.get("lastStatus")
            records_all_supported = recording_group.get("allSupported", False)
            includes_global = recording_group.get("includeGlobalResources", False)
            has_delivery_channel = bool(delivery_channels)
            compliant = (
                recording
                and last_status == "SUCCESS"
                and records_all_supported
                and has_delivery_channel
            )

            all_details.append(
                {
                    "region": region,
                    "config_enabled": compliant,
                    "recording": recording,
                    "last_status": last_status,
                    "records_all_supported_resources": records_all_supported,
                    "include_global_resources": includes_global,
                    "has_delivery_channel": has_delivery_channel,
                }
            )

            if compliant:
                compliant_regions.append(region)
                if includes_global:
                    global_resource_regions.append(region)
            else:
                noncompliant_regions.append(region)
        except Exception as exc:
            logger.warning("Error checking AWS Config in %s: %s", region, exc)
            all_details.append({"region": region, "error": str(exc)})
            noncompliant_regions.append(region)

    has_global_resource_recording = bool(global_resource_regions)
    status = "PASS" if not noncompliant_regions and has_global_resource_recording else "FAIL"
    reason = None
    if noncompliant_regions:
        reason = "AWS Config is not fully enabled in all selected regions"
    elif not has_global_resource_recording:
        reason = "Global resources are not recorded in any selected region"

    details = {
        "config_enabled_regions": compliant_regions,
        "config_disabled_regions": noncompliant_regions,
        "global_resources_regions": global_resource_regions,
        "by_region": all_details,
    }
    if reason:
        details["reason"] = reason

    return create_result(
        control_id,
        control["title"],
        status,
        control["severity"],
        details=details,
        resource_id=",".join(compliant_regions) if compliant_regions else None,
        remediation="Enable AWS Config in every region, record all supported resources, configure a delivery channel, and record global resources in at least one region" if status == "FAIL" else None,
    )
