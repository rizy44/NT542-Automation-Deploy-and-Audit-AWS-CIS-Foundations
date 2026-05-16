"""
CIS 6.5: Ensure the default security group of every VPC restricts all traffic (Automated)
"""
import logging

from scripts.Ver_Network.config import NETWORK_CONTROLS, get_client, get_all_regions
from scripts.Ver_Network.utils import create_result, error_handler

logger = logging.getLogger(__name__)


@error_handler
def check_control_6_5(profile_name=None, regions=None, **kwargs):
    control_id = "6.5"
    control = NETWORK_CONTROLS[control_id]

    if not regions:
        regions = get_all_regions(profile_name=profile_name)

    all_details = []
    compliant_default_sgs = []
    noncompliant_default_sgs = []

    for region in regions:
        try:
            ec2_client = get_client("ec2", region_name=region, profile_name=profile_name)
            response = ec2_client.describe_security_groups(
                Filters=[{"Name": "group-name", "Values": ["default"]}]
            )

            for sg in response.get("SecurityGroups", []):
                ingress_rules = sg.get("IpPermissions", [])
                egress_rules = sg.get("IpPermissionsEgress", [])

                is_restrictive = len(ingress_rules) == 0 and len(egress_rules) == 0

                sg_info = {
                    "region": region,
                    "sg_id": sg.get("GroupId"),
                    "vpc_id": sg.get("VpcId"),
                    "ingress_count": len(ingress_rules),
                    "egress_count": len(egress_rules),
                    "is_restrictive": is_restrictive,
                }
                all_details.append(sg_info)

                if is_restrictive:
                    compliant_default_sgs.append(sg.get("GroupId"))
                else:
                    noncompliant_default_sgs.append(sg.get("GroupId"))
        except Exception as e:
            logger.warning(f"Could not check default security groups in region {region}: {str(e)}")

    status = "PASS" if not noncompliant_default_sgs else "FAIL"

    return create_result(
        control_id,
        control["title"],
        status,
        control["severity"],
        details={
            "compliant_default_sgs": compliant_default_sgs,
            "noncompliant_default_sgs": noncompliant_default_sgs,
            "by_security_group": all_details,
        },
        resource_id=",".join(compliant_default_sgs) if compliant_default_sgs else None,
        remediation="Remove all inbound and outbound rules from default security groups" if status == "FAIL" else None,
    )
