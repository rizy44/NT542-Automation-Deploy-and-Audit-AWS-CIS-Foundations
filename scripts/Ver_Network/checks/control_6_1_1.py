"""
CIS 6.1.1: Ensure EBS volume encryption is enabled in all regions (Automated)
"""
import logging

from scripts.Ver_Network.config import NETWORK_CONTROLS, get_client, get_all_regions
from scripts.Ver_Network.utils import create_result, error_handler

logger = logging.getLogger(__name__)


@error_handler
def check_control_6_1_1(profile_name=None, regions=None, **kwargs):
    control_id = "6.1.1"
    control = NETWORK_CONTROLS[control_id]

    if not regions:
        regions = get_all_regions(profile_name=profile_name)

    all_details = []
    regions_with_encryption = []
    regions_without_encryption = []

    for region in regions:
        try:
            ec2_client = get_client("ec2", region_name=region, profile_name=profile_name)
            response = ec2_client.get_ebs_encryption_by_default()
            ebs_encryption_enabled = response.get("EbsEncryptionByDefault", False)

            region_info = {
                "region": region,
                "ebs_encryption_enabled": ebs_encryption_enabled,
            }
            all_details.append(region_info)

            if ebs_encryption_enabled:
                regions_with_encryption.append(region)
            else:
                regions_without_encryption.append(region)
        except Exception as e:
            logger.warning(f"Could not check EBS encryption in region {region}: {str(e)}")
            region_info = {
                "region": region,
                "error": str(e),
            }
            all_details.append(region_info)
            regions_without_encryption.append(region)

    status = "PASS" if not regions_without_encryption else "FAIL"

    return create_result(
        control_id,
        control["title"],
        status,
        control["severity"],
        details={
            "regions_with_encryption": regions_with_encryption,
            "regions_without_encryption": regions_without_encryption,
            "by_region": all_details,
        },
        resource_id=",".join(regions_with_encryption) if regions_with_encryption else None,
        remediation="Enable EBS encryption by default in all regions" if status == "FAIL" else None,
    )
