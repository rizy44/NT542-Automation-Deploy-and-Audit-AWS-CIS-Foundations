"""
CIS 4.7: Ensure VPC flow logging is enabled in all VPCs.
"""
import logging

from scripts.Ver_Cloudtrail.config import CIS_CONTROLS, get_all_regions, get_client
from scripts.Ver_Cloudtrail.utils import create_result, error_handler

logger = logging.getLogger(__name__)


@error_handler
def check_control_4_7(profile_name=None, regions=None):
    control_id = "4.7"
    control = CIS_CONTROLS[control_id]
    if not regions:
        regions = get_all_regions(profile_name=profile_name)

    all_details = []
    vpcs_with_logs = []
    vpcs_without_logs = []

    for region in regions:
        try:
            ec2_client = get_client("ec2", region_name=region, profile_name=profile_name)
            vpcs = ec2_client.describe_vpcs().get("Vpcs", [])
            flow_logs = ec2_client.describe_flow_logs().get("FlowLogs", [])
            vpc_ids_with_logs = {
                log.get("ResourceId")
                for log in flow_logs
                if log.get("ResourceType") == "VPC" and log.get("FlowLogStatus") != "FAILED"
            }

            for vpc in vpcs:
                vpc_id = vpc.get("VpcId")
                has_flow_logs = vpc_id in vpc_ids_with_logs
                all_details.append(
                    {
                        "region": region,
                        "vpc_id": vpc_id,
                        "has_flow_logs": has_flow_logs,
                    }
                )
                if has_flow_logs:
                    vpcs_with_logs.append(f"{region}:{vpc_id}")
                else:
                    vpcs_without_logs.append(f"{region}:{vpc_id}")
        except Exception as exc:
            logger.warning("Error checking VPC Flow Logs in %s: %s", region, exc)
            all_details.append({"region": region, "error": str(exc)})

    status = "PASS" if not vpcs_without_logs else "FAIL"
    return create_result(
        control_id,
        control["title"],
        status,
        control["severity"],
        details={
            "vpcs_with_logs": len(vpcs_with_logs),
            "vpcs_without_logs": len(vpcs_without_logs),
            "noncompliant_vpcs": vpcs_without_logs,
            "by_vpc": all_details,
        },
        resource_id=",".join(vpcs_with_logs) if vpcs_with_logs else None,
        remediation="Enable VPC Flow Logs for every VPC" if status == "FAIL" else None,
    )
