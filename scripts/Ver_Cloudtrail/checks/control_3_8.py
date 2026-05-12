"""
CIS 3.8: Ensure S3 object-level logging for WRITE events is enabled
"""
import logging
from scripts.Ver_Cloudtrail.config import get_client, CIS_CONTROLS
from scripts.Ver_Cloudtrail.utils import create_result, error_handler

logger = logging.getLogger(__name__)

@error_handler
def check_control_3_8(profile_name=None, regions=None):
    """
    Check if S3 object-level logging for WRITE events is enabled
    
    Verifies:
    - CloudTrail has data events configured
    - Resource type includes S3
    - ReadWriteType includes WriteOnly or All
    
    Args:
        profile_name: AWS profile name
        regions: List of regions to check (if None, checks all regions)
    
    Returns:
        dict with control result
    """
    control_id = "3.8"
    control = CIS_CONTROLS[control_id]
    
    try:
        cloudtrail_client = get_client('cloudtrail', profile_name=profile_name)
        
        # Describe trails
        response = cloudtrail_client.describe_trails(includeShadowTrails=False)
        trails = response.get('trailList', [])
        
        if not trails:
            return create_result(
                control_id,
                control['title'],
                'FAIL',
                control['severity'],
                details={"reason": "No CloudTrail trails found"},
                remediation="Enable S3 object-level logging for WRITE events"
            )
        
        all_details = []
        trails_with_write_logging = []
        trails_without_write_logging = []
        
        for trail in trails:
            trail_name = trail.get('Name')
            trail_arn = trail.get('TrailARN')
            
            # Get event selectors to check data events
            try:
                event_selectors_response = cloudtrail_client.get_event_selectors(TrailName=trail_arn)
                event_selectors = event_selectors_response.get('EventSelectors', [])
                data_resources = event_selectors_response.get('EventSelectors', [])[0].get('DataResources', []) if event_selectors else []
                
                has_write_logging = False
                
                for data_resource in data_resources:
                    resource_type = data_resource.get('Type')
                    read_write_type = data_resource.get('Values')
                    
                    # Check if S3 object logging is enabled with WriteOnly or All
                    if resource_type == 'AWS::S3::Object':
                        if read_write_type and any(t in ['WriteOnly', 'All'] for t in read_write_type):
                            has_write_logging = True
                
                trail_info = {
                    "trail_name": trail_name,
                    "trail_arn": trail_arn,
                    "has_s3_write_logging": has_write_logging,
                    "data_resources": [
                        {
                            "type": dr.get('Type'),
                            "values": dr.get('Values', [])
                        }
                        for dr in data_resources
                    ]
                }
                all_details.append(trail_info)
                
                if has_write_logging:
                    trails_with_write_logging.append(trail_name)
                else:
                    trails_without_write_logging.append(trail_name)
            
            except Exception as e:
                logger.warning(f"Could not get event selectors for {trail_name}: {str(e)}")
                trail_info = {
                    "trail_name": trail_name,
                    "error": str(e)
                }
                all_details.append(trail_info)
                trails_without_write_logging.append(trail_name)
        
        if trails_without_write_logging:
            status = 'FAIL'
            details = {
                "trails_with_write_logging": trails_with_write_logging,
                "trails_without_write_logging": trails_without_write_logging,
                "all_trails": all_details
            }
        else:
            status = 'PASS'
            details = {
                "trails_with_write_logging": trails_with_write_logging,
                "all_trails": all_details
            }
        
        return create_result(
            control_id,
            control['title'],
            status,
            control['severity'],
            details=details,
            resource_id=','.join(trails_with_write_logging) if trails_with_write_logging else None,
            remediation="Enable S3 object-level logging for WRITE events in all trails" if status == 'FAIL' else None
        )
    
    except Exception as e:
        logger.error(f"Error checking control 3.8: {str(e)}")
        return create_result(
            control_id,
            control['title'],
            'UNKNOWN',
            control['severity'],
            details={"error": str(e)}
        )
