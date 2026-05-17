"""
CIS 6.6: Ensure routing tables for VPC peering are least access (Manual)

Enhanced diagnostics:
- Uses paginator for describe_route_tables to avoid missing results
- Detects peering via `VpcPeeringConnectionId` or `GatewayId` starting with "pcx-"
- Catches and logs IAM/connection errors
- Enforces region `ap-southeast-1`
"""
import logging
from typing import List

import botocore.exceptions

from scripts.Ver_Network.config import NETWORK_CONTROLS, get_client, get_all_regions
from scripts.Ver_Network.utils import create_result, error_handler

logger = logging.getLogger(__name__)


@error_handler
def check_control_6_6(profile_name: str = None, regions: List[str] = None, **kwargs):
    """
    Manual check with enhanced diagnostics.

    Notes:
    - This function enforces `ap-southeast-1` as the target region for the lab.
    - It uses a paginator to enumerate all route tables.
    - It checks for both `VpcPeeringConnectionId` and a `GatewayId` that starts with `pcx-`.
    """
    control_id = "6.6"
    control = NETWORK_CONTROLS[control_id]

    # Enforce lab region
    regions = ["ap-southeast-1"]

    all_details = []

    for region in regions:
        try:
            ec2_client = get_client("ec2", region_name=region, profile_name=profile_name)

            paginator = ec2_client.get_paginator("describe_route_tables")
            page_iterator = paginator.paginate()

            for page in page_iterator:
                for route_table in page.get("RouteTables", []):
                    peering_routes = []

                    for route in route_table.get("Routes", []):
                        # Primary indicator used by AWS for peering routes
                        vpc_peering_id = route.get("VpcPeeringConnectionId")
                        if vpc_peering_id:
                            peering_routes.append({
                                "destination": route.get("DestinationCidrBlock") or route.get("DestinationIpv6CidrBlock") or route.get("DestinationPrefixListId"),
                                "peering_id": vpc_peering_id,
                                "match_type": "VpcPeeringConnectionId",
                            })
                            continue

                        # Some routes may place the peering id in GatewayId (detect pcx-*)
                        gateway_id = route.get("GatewayId") or ""
                        if isinstance(gateway_id, str) and gateway_id.startswith("pcx-"):
                            peering_routes.append({
                                "destination": route.get("DestinationCidrBlock") or route.get("DestinationIpv6CidrBlock") or route.get("DestinationPrefixListId"),
                                "peering_id": gateway_id,
                                "match_type": "GatewayId",
                            })

                    if peering_routes:
                        rt_info = {
                            "region": region,
                            "route_table_id": route_table.get("RouteTableId"),
                            "vpc_id": route_table.get("VpcId"),
                            "peering_routes": peering_routes,
                        }
                        all_details.append(rt_info)

        except botocore.exceptions.ClientError as e:
            # Likely IAM permission issue or API error — log details for diagnosis
            err = e.response.get("Error", {}) if hasattr(e, "response") else {}
            logger.error("AWS ClientError checking route tables in %s: %s %s", region, err.get("Code"), err.get("Message"))
        except botocore.exceptions.EndpointConnectionError as e:
            logger.error("Endpoint connection error for region %s: %s", region, str(e))
        except Exception:
            logger.exception("Unexpected error while checking route tables in %s", region)

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
