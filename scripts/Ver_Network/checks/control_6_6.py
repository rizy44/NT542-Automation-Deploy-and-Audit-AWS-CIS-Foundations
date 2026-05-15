"""
CIS 6.6: Ensure routing tables for VPC peering are least access (Manual)
"""
import logging

from scripts.Ver_Network.config import NETWORK_CONTROLS, get_client, get_all_regions
from scripts.Ver_Network.utils import create_result, error_handler

logger = logging.getLogger(__name__)


@error_handler
def check_control_6_6(profile_name=None, regions=None, **kwargs):
    """
    Manual check: Review peering routes to ensure least privilege access.
    This is marked as UNKNOWN since it requires manual review of routing policy.
    """
    control_id = "6.6"
    control = NETWORK_CONTROLS[control_id]

    if not regions:
        regions = get_all_regions(profile_name=profile_name)

    all_details = []

    for region in regions:
        try:
            ec2_client = get_client("ec2", region_name=region, profile_name=profile_name)
            response = ec2_client.describe_route_tables()

            for route_table in response.get("RouteTables", []):
                peering_routes = []
                for route in route_table.get("Routes", []):
                    if "VpcPeeringConnectionId" in route:
                        peering_routes.append({
                            "destination": route.get("DestinationCidrBlock"),
                            "peering_id": route.get("VpcPeeringConnectionId"),
                        })

                if peering_routes:
                    rt_info = {
                        "region": region,
                        "route_table_id": route_table.get("RouteTableId"),
                        "vpc_id": route_table.get("VpcId"),
                        "peering_routes": peering_routes,
                    }
                    all_details.append(rt_info)
        except Exception as e:
            logger.warning(f"Could not check routing tables in region {region}: {str(e)}")

    return create_result(
        control_id,
        control["title"],
        "UNKNOWN",
        control["severity"],
        details={
            "reason": "Manual check required - review peering routes to ensure least access principle is followed",
            "peering_routes_found": all_details,
        },
        remediation="Review routing tables and ensure VPC peering routes follow least privilege principle",
    )
