"""
CIS 3.1: Ensure CloudTrail is enabled in all regions
"""
import logging
from config import get_client, get_all_regions, CIS_CONTROLS
from utils import create_result, error_handler

logger = logging.getLogger(__name__)

@error_handler
def check_control_3_1(profile_name=None, regions=None):
    """
    Check if CloudTrail is enabled in all regions
    
    Verifies:
    - At least one trail exists
    - IsMultiRegionTrail = true
    - IsLogging = true
    - IncludeGlobalServiceEvents = true
    
    Args:
        profile_name: AWS profile name
        regions: List of regions to check (if None, checks all regions)
    
    Returns:
        dict with control result
    """
    control_id = "3.1"
    control = CIS_CONTROLS[control_id]
    
    try:
        # Get CloudTrail client (regional client in home region)
        cloudtrail_client = get_client('cloudtrail', profile_name=profile_name)
        
        # Describe trails
        response = cloudtrail_client.describe_trails(includeShadowTrails=False)
        trails = response.get('trailList', [])
        
        if not trails:
            logger.warning("No CloudTrail trails found")
            return create_result(
                control_id,
                control['title'],
                'FAIL',
                control['severity'],
                details={"reason": "No CloudTrail trails configured"},
                remediation="Enable CloudTrail with multi-region and logging enabled"
            )
        
        # Check for multi-region trail with logging enabled
        multi_region_trails = []
        all_details = []
        
        for trail in trails:
            trail_info = {
                "trail_name": trail.get('Name'),
                "arn": trail.get('TrailARN'),
                "is_multi_region": trail.get('IsMultiRegionTrail', False),
                "include_global_events": trail.get('IncludeGlobalServiceEvents', False)
            }
            
            # Check trail status (logging enabled)
            try:
                trail_status = cloudtrail_client.get_trail_status(Name=trail['TrailARN'])
                trail_info['is_logging'] = trail_status.get('IsLogging', False)
            except Exception as e:
                logger.warning(f"Could not get status for trail {trail.get('Name')}: {str(e)}")
                trail_info['is_logging'] = False
            
            all_details.append(trail_info)
            
            # Check if trail meets criteria
            if (trail.get('IsMultiRegionTrail') and 
                trail_info['is_logging'] and 
                trail.get('IncludeGlobalServiceEvents')):
                multi_region_trails.append(trail.get('Name'))
        
        if multi_region_trails:
            status = 'PASS'
            details = {
                "multi_region_trails": multi_region_trails,
                "all_trails": all_details
            }
        else:
            status = 'FAIL'
            details = {
                "reason": "No multi-region trail with logging enabled",
                "all_trails": all_details,
                "remediation": "Enable multi-region CloudTrail with logging and global service events"
            }
        
        return create_result(
            control_id,
            control['title'],
            status,
            control['severity'],
            details=details,
            resource_id=','.join(multi_region_trails) if multi_region_trails else None,
            remediation="Enable CloudTrail in multi-region mode with logging enabled" if status == 'FAIL' else None
        )
    
    except Exception as e:
        logger.error(f"Error checking control 3.1: {str(e)}")
        return create_result(
            control_id,
            control['title'],
            'UNKNOWN',
            control['severity'],
            details={"error": str(e)}
        )
