"""
CIS 6.4: Ensure no security groups allow ingress from ::/0 to SSH/RDP (Automated)
"""
import logging

from scripts.Ver_Network.config import NETWORK_CONTROLS, get_client, get_all_regions
from scripts.Ver_Network.utils import create_result, error_handler

logger = logging.getLogger(__name__)


def has_unrestricted_ssh_rdp_ipv6(security_group):
    """Check if SG allows SSH/RDP from ::/0"""
    for rule in security_group.get("IpPermissions", []):
        from_port = rule.get("FromPort")
        to_port = rule.get("ToPort")
        protocol = str(rule.get("IpProtocol", ""))

        if protocol in ["-1"]:
            for ip_range in rule.get("Ipv6Ranges", []):
                if ip_range.get("CidrIpv6") == "::/0":
                    return True

        if from_port in [22, 3389] and to_port == from_port:
            for ip_range in rule.get("Ipv6Ranges", []):
                if ip_range.get("CidrIpv6") == "::/0":
                    return True

    return False


@error_handler
def check_control_6_4(profile_name=None, regions=None, **kwargs):
    control_id = "6.4"
    control = NETWORK_CONTROLS[control_id]

    if not regions:
        regions = get_all_regions(profile_name=profile_name)

    all_details = []
    compliant_sgs = []
    noncompliant_sgs = []

    for region in regions:
        try:
            ec2_client = get_client("ec2", region_name=region, profile_name=profile_name)
            response = ec2_client.describe_security_groups()

            for sg in response.get("SecurityGroups", []):
                is_compliant = not has_unrestricted_ssh_rdp_ipv6(sg)

                sg_info = {
                    "region": region,
                    "sg_id": sg.get("GroupId"),
                    "sg_name": sg.get("GroupName"),
                    "vpc_id": sg.get("VpcId"),
                    "has_unrestricted_access": not is_compliant,
                }
                all_details.append(sg_info)

                if is_compliant:
                    compliant_sgs.append(sg.get("GroupId"))
                else:
                    noncompliant_sgs.append(sg.get("GroupId"))
        except Exception as e:
            logger.warning(f"Could not check security groups in region {region}: {str(e)}")

    status = "PASS" if not noncompliant_sgs else "FAIL"

    return create_result(
        control_id,
        control["title"],
        status,
        control["severity"],
        details={
            "compliant_security_groups": compliant_sgs,
            "noncompliant_security_groups": noncompliant_sgs,
            "by_security_group": all_details,
        },
        resource_id=",".join(compliant_sgs) if compliant_sgs else None,
        remediation="Remove security group rules allowing SSH/RDP from ::/0" if status == "FAIL" else None,
    )
