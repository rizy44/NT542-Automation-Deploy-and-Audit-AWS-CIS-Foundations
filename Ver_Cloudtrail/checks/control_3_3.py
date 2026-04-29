"""
CIS 3.3: Ensure S3 bucket access logging is enabled
"""
import logging
from config import get_client, CIS_CONTROLS
from utils import create_result, error_handler

logger = logging.getLogger(__name__)

@error_handler
def check_control_3_3(profile_name=None, regions=None):
    """
    Check if S3 bucket access logging is enabled for CloudTrail bucket
    
    Verifies:
    - S3 bucket used by CloudTrail has access logging enabled
    - Target bucket and prefix are configured
    
    Args:
        profile_name: AWS profile name
        regions: List of regions to check (if None, checks all regions)
    
    Returns:
        dict with control result
    """
    control_id = "3.3"
    control = CIS_CONTROLS[control_id]
    
    try:
        cloudtrail_client = get_client('cloudtrail', profile_name=profile_name)
        s3_client = get_client('s3', profile_name=profile_name)
        
        # Describe trails to get S3 bucket
        response = cloudtrail_client.describe_trails(includeShadowTrails=False)
        trails = response.get('trailList', [])
        
        if not trails:
            return create_result(
                control_id,
                control['title'],
                'FAIL',
                control['severity'],
                details={"reason": "No CloudTrail trails found"},
                remediation="Enable CloudTrail and configure S3 access logging"
            )
        
        all_details = []
        logging_enabled_buckets = []
        logging_disabled_buckets = []
        
        for trail in trails:
            s3_bucket_name = trail.get('S3BucketName')
            if not s3_bucket_name:
                continue
            
            try:
                # Check bucket logging configuration
                logging_config = s3_client.get_bucket_logging(Bucket=s3_bucket_name)
                logging_rules = logging_config.get('LoggingEnabled', {})
                
                bucket_info = {
                    "bucket_name": s3_bucket_name,
                    "trail_name": trail.get('Name'),
                    "logging_enabled": bool(logging_rules),
                    "target_bucket": logging_rules.get('TargetBucket') if logging_rules else None,
                    "target_prefix": logging_rules.get('TargetPrefix') if logging_rules else None
                }
                all_details.append(bucket_info)
                
                if logging_rules:
                    logging_enabled_buckets.append(s3_bucket_name)
                else:
                    logging_disabled_buckets.append(s3_bucket_name)
            
            except Exception as e:
                logger.warning(f"Could not check logging for bucket {s3_bucket_name}: {str(e)}")
                bucket_info = {
                    "bucket_name": s3_bucket_name,
                    "trail_name": trail.get('Name'),
                    "error": str(e)
                }
                all_details.append(bucket_info)
                logging_disabled_buckets.append(s3_bucket_name)
        
        if logging_disabled_buckets:
            status = 'FAIL'
            details = {
                "logging_enabled_buckets": logging_enabled_buckets,
                "logging_disabled_buckets": logging_disabled_buckets,
                "all_details": all_details
            }
        else:
            status = 'PASS'
            details = {
                "logging_enabled_buckets": logging_enabled_buckets,
                "all_details": all_details
            }
        
        return create_result(
            control_id,
            control['title'],
            status,
            control['severity'],
            details=details,
            resource_id=','.join(logging_enabled_buckets) if logging_enabled_buckets else None,
            remediation="Enable S3 access logging for CloudTrail buckets" if status == 'FAIL' else None
        )
    
    except Exception as e:
        logger.error(f"Error checking control 3.3: {str(e)}")
        return create_result(
            control_id,
            control['title'],
            'UNKNOWN',
            control['severity'],
            details={"error": str(e)}
        )
