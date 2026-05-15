"""
CIS 6.1.2: Ensure CIFS access is restricted to trusted networks (Automated)
"""
import logging

from scripts.Ver_Network.config import NETWORK_CONTROLS, get_client, get_project_vpcs
from scripts.Ver_Network.utils import create_result, error_handler

logger = logging.getLogger(__name__)


@error_handler
def check_control_6_1_2(profile_name=None, regions=None, **kwargs):
    control_id = "6.1.2"
    control = NETWORK_CONTROLS[control_id]

    vpcs = get_project_vpcs(
        profile_name=profile_name,
        regions=regions,
    )

    if not vpcs:
        return create_result(
            control_id,
            control["title"],
            "PASS",
            control["severity"],
            details={"reason": "No VPCs found"},
        )

    all_details = []
    compliant_sgs = []
    noncompliant_sgs = []

    for vpc in vpcs:
        ec2_client = get_client("ec2", region_name=vpc["region"], profile_name=profile_name)
        response = ec2_client.describe_security_groups(Filters=[{"Name": "vpc-id", "Values": [vpc["VpcId"]]}])

        for sg in response.get("SecurityGroups", []):
            cifs_unrestricted = False
            for rule in sg.get("IpPermissions", []):
                from_port = rule.get("FromPort")
                to_port = rule.get("ToPort")
                protocol = str(rule.get("IpProtocol", ""))

                if protocol == "-1" or (from_port is not None and to_port is not None and from_port <= 445 <= to_port):
                    for ip_range in rule.get("IpRanges", []):
                        if ip_range.get("CidrIp") == "0.0.0.0/0":
                            cifs_unrestricted = True
                    for ip_range in rule.get("Ipv6Ranges", []):
                        if ip_range.get("CidrIpv6") == "::/0":
                            cifs_unrestricted = True

            sg_info = {
                "region": vpc["region"],
                "vpc_id": vpc["VpcId"],
                "sg_id": sg.get("GroupId"),
                "sg_name": sg.get("GroupName"),
                "cifs_unrestricted": cifs_unrestricted,
            }
            all_details.append(sg_info)

            if not cifs_unrestricted:
                compliant_sgs.append(sg.get("GroupId"))
            else:
                noncompliant_sgs.append(sg.get("GroupId"))

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
        remediation="Restrict CIFS (port 445) access from 0.0.0.0/0 in security groups" if status == "FAIL" else None,
    )
