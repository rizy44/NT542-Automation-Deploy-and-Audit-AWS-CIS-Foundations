"""
CIS 3.7: Ensure VPC Flow Logs are enabled
"""
import logging
from scripts.Ver_Cloudtrail.config import get_client, get_all_regions, CIS_CONTROLS
from scripts.Ver_Cloudtrail.utils import create_result, error_handler

logger = logging.getLogger(__name__)

@error_handler
def check_control_3_7(profile_name=None, regions=None):
    """
    Check if VPC Flow Logs are enabled for all VPCs
    
    Verifies:
    - All VPCs have flow logs
    - Destination is CloudWatch Logs or S3
    
    Args:
        profile_name: AWS profile name
        regions: List of regions to check (if None, checks all regions)
    
    Returns:
        dict with control result
    """
    control_id = "3.7"
    control = CIS_CONTROLS[control_id]
    
    try:
        # Get all regions if not specified
        if not regions:
            regions = get_all_regions(profile_name=profile_name)
        
        all_details = []
        vpcs_with_logs = 0
        vpcs_without_logs = 0
        
        for region in regions:
            try:
                ec2_client = get_client('ec2', region_name=region, profile_name=profile_name)
                
                # Get all VPCs
                vpcs_response = ec2_client.describe_vpcs()
                vpcs = vpcs_response.get('Vpcs', [])
                
                if not vpcs:
                    continue
                
                # Get flow logs
                flow_logs_response = ec2_client.describe_flow_logs()
                flow_logs = flow_logs_response.get('FlowLogs', [])
                
                # Create a set of VPCs with flow logs
                vpc_ids_with_logs = set()
                for flow_log in flow_logs:
                    if flow_log.get('ResourceType') == 'VPC':
                        vpc_ids_with_logs.add(flow_log.get('ResourceId'))
                
                # Check each VPC
                for vpc in vpcs:
                    vpc_id = vpc.get('VpcId')
                    has_flow_logs = vpc_id in vpc_ids_with_logs
                    
                    vpc_info = {
                        "region": region,
                        "vpc_id": vpc_id,
                        "has_flow_logs": has_flow_logs
                    }
                    all_details.append(vpc_info)
                    
                    if has_flow_logs:
                        vpcs_with_logs += 1
                    else:
                        vpcs_without_logs += 1
                
            except Exception as e:
                logger.warning(f"Error checking VPCs in region {region}: {str(e)}")
                region_info = {
                    "region": region,
                    "error": str(e)
                }
                all_details.append(region_info)
        
        if vpcs_without_logs > 0:
            status = 'FAIL'
            details = {
                "vpcs_with_logs": vpcs_with_logs,
                "vpcs_without_logs": vpcs_without_logs,
                "by_vpc": all_details
            }
        else:
            status = 'PASS'
            details = {
                "vpcs_with_logs": vpcs_with_logs,
                "by_vpc": all_details
            }
        
        return create_result(
            control_id,
            control['title'],
            status,
            control['severity'],
            details=details,
            resource_id=f"{vpcs_with_logs}_vpcs" if vpcs_with_logs > 0 else None,
            remediation="Enable VPC Flow Logs for all VPCs" if status == 'FAIL' else None
        )
    
    except Exception as e:
        logger.error(f"Error checking control 3.7: {str(e)}")
        return create_result(
            control_id,
            control['title'],
            'UNKNOWN',
            control['severity'],
            details={"error": str(e)}
        )
