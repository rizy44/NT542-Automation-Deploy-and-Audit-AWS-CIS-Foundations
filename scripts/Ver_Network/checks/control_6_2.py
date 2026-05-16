"""
CIS 6.2: Ensure no Network ACLs allow ingress from 0.0.0.0/0 to remote server admin ports (Automated)
"""
import logging

from scripts.Ver_Network.config import NETWORK_CONTROLS, get_client, get_all_regions
from scripts.Ver_Network.utils import create_result, error_handler

logger = logging.getLogger(__name__)


def is_dangerous_nacl_rule(rule):
    """Check if NACL rule allows SSH/RDP from 0.0.0.0/0"""
    if rule.get("Egress"):
        return False

    cidr_block = rule.get("CidrBlock")
    if cidr_block != "0.0.0.0/0":
        return False

    protocol = str(rule.get("Protocol", ""))
    from_port = rule.get("PortRange", {}).get("From")
    to_port = rule.get("PortRange", {}).get("To")

    if protocol == "-1":
        return True
    if from_port == 22 and to_port == 22:
        return True
    if from_port == 3389 and to_port == 3389:
        return True

    return False


@error_handler
def check_control_6_2(profile_name=None, regions=None, **kwargs):
    control_id = "6.2"
    control = NETWORK_CONTROLS[control_id]

    if not regions:
        regions = get_all_regions(profile_name=profile_name)

    all_details = []
    compliant_nacls = []
    noncompliant_nacls = []

    for region in regions:
        try:
            ec2_client = get_client("ec2", region_name=region, profile_name=profile_name)
            response = ec2_client.describe_network_acls()

            for nacl in response.get("NetworkAcls", []):
                has_dangerous_rules = False
                dangerous_rules = []

                for entry in nacl.get("Entries", []):
                    if is_dangerous_nacl_rule(entry):
                        has_dangerous_rules = True
                        dangerous_rules.append({
                            "rule_number": entry.get("RuleNumber"),
                            "protocol": entry.get("Protocol"),
                            "port_range": entry.get("PortRange"),
                        })

                nacl_info = {
                    "region": region,
                    "nacl_id": nacl.get("NetworkAclId"),
                    "has_dangerous_rules": has_dangerous_rules,
                    "dangerous_rules": dangerous_rules,
                }
                all_details.append(nacl_info)

                if not has_dangerous_rules:
                    compliant_nacls.append(nacl.get("NetworkAclId"))
                else:
                    noncompliant_nacls.append(nacl.get("NetworkAclId"))
        except Exception as e:
            logger.warning(f"Could not check NACLs in region {region}: {str(e)}")

    status = "PASS" if not noncompliant_nacls else "FAIL"

    return create_result(
        control_id,
        control["title"],
        status,
        control["severity"],
        details={
            "compliant_nacls": compliant_nacls,
            "noncompliant_nacls": noncompliant_nacls,
            "by_nacl": all_details,
        },
        resource_id=",".join(compliant_nacls) if compliant_nacls else None,
        remediation="Remove NACL rules that allow SSH/RDP from 0.0.0.0/0" if status == "FAIL" else None,
    )
