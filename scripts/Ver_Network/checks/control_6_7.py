"""
CIS 6.7: Ensure that the EC2 Metadata Service only allows IMDSv2 (Automated)
"""
import logging

from scripts.Ver_Network.config import NETWORK_CONTROLS, get_client, get_all_regions
from scripts.Ver_Network.utils import create_result, error_handler

logger = logging.getLogger(__name__)


@error_handler
def check_control_6_7(profile_name=None, regions=None, **kwargs):
    control_id = "6.7"
    control = NETWORK_CONTROLS[control_id]

    if not regions:
        regions = get_all_regions(profile_name=profile_name)

    all_details = []
    imdsv2_required_instances = []
    imdsv2_not_required_instances = []

    for region in regions:
        try:
            ec2_client = get_client("ec2", region_name=region, profile_name=profile_name)
            response = ec2_client.describe_instances()

            for reservation in response.get("Reservations", []):
                for instance in reservation.get("Instances", []):
                    metadata_options = instance.get("MetadataOptions", {})
                    http_tokens = metadata_options.get("HttpTokens")
                    state = metadata_options.get("State")

                    is_compliant = http_tokens == "required" and state == "applied"

                    instance_info = {
                        "region": region,
                        "instance_id": instance.get("InstanceId"),
                        "http_tokens": http_tokens,
                        "state": state,
                        "is_imdsv2_required": is_compliant,
                    }
                    all_details.append(instance_info)

                    if is_compliant:
                        imdsv2_required_instances.append(instance.get("InstanceId"))
                    else:
                        imdsv2_not_required_instances.append(instance.get("InstanceId"))
        except Exception as e:
            logger.warning(f"Could not check instances in region {region}: {str(e)}")

    status = "PASS" if not imdsv2_not_required_instances else "FAIL"

    return create_result(
        control_id,
        control["title"],
        status,
        control["severity"],
        details={
            "imdsv2_required_instances": imdsv2_required_instances,
            "imdsv2_not_required_instances": imdsv2_not_required_instances,
            "by_instance": all_details,
        },
        resource_id=",".join(imdsv2_required_instances) if imdsv2_required_instances else None,
        remediation="Set IMDSv2 as Required on all EC2 instances to prevent SSRF attacks" if status == "FAIL" else None,
    )
