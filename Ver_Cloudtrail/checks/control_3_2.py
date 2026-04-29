"""
CIS 3.2: Ensure log file validation is enabled
"""
import logging
from config import get_client, CIS_CONTROLS
from utils import create_result, error_handler

logger = logging.getLogger(__name__)

@error_handler
def check_control_3_2(profile_name=None, regions=None):
    """
    Check if CloudTrail log file validation is enabled
    
    Verifies:
    - LogFileValidationEnabled = true for each trail
    
    Args:
        profile_name: AWS profile name
        regions: List of regions to check (if None, checks all regions)
    
    Returns:
        dict with control result
    """
    control_id = "3.2"
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
                remediation="Enable log file validation for CloudTrail trails"
            )
        
        all_details = []
        validated_trails = []
        failed_trails = []
        
        for trail in trails:
            trail_info = {
                "trail_name": trail.get('Name'),
                "arn": trail.get('TrailARN'),
                "log_file_validation_enabled": trail.get('LogFileValidationEnabled', False)
            }
            all_details.append(trail_info)
            
            if trail.get('LogFileValidationEnabled'):
                validated_trails.append(trail.get('Name'))
            else:
                failed_trails.append(trail.get('Name'))
        
        if failed_trails:
            status = 'FAIL'
            details = {
                "validated_trails": validated_trails,
                "unvalidated_trails": failed_trails,
                "all_trails": all_details
            }
        else:
            status = 'PASS'
            details = {
                "validated_trails": validated_trails,
                "all_trails": all_details
            }
        
        return create_result(
            control_id,
            control['title'],
            status,
            control['severity'],
            details=details,
            resource_id=','.join(validated_trails) if validated_trails else None,
            remediation="Enable log file validation for all CloudTrail trails" if status == 'FAIL' else None
        )
    
    except Exception as e:
        logger.error(f"Error checking control 3.2: {str(e)}")
        return create_result(
            control_id,
            control['title'],
            'UNKNOWN',
            control['severity'],
            details={"error": str(e)}
        )
