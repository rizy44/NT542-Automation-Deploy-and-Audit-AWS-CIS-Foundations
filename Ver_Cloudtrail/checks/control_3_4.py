"""
CIS 3.4: Ensure CloudTrail logs are encrypted with KMS CMK
"""
import logging
from config import get_client, CIS_CONTROLS
from utils import create_result, error_handler

logger = logging.getLogger(__name__)

def is_customer_managed_key(key_id):
    """
    Check if KMS key ID is a customer-managed key
    Customer-managed keys have ARN format: arn:aws:kms:region:account:key/key-id
    """
    if not key_id:
        return False
    return key_id.startswith('arn:aws:kms:')

@error_handler
def check_control_3_4(profile_name=None, regions=None):
    """
    Check if CloudTrail logs are encrypted with KMS CMK
    
    Verifies:
    - KmsKeyId exists
    - Key is customer-managed (CMK), not AWS-managed
    
    Args:
        profile_name: AWS profile name
        regions: List of regions to check (if None, checks all regions)
    
    Returns:
        dict with control result
    """
    control_id = "3.4"
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
                remediation="Enable CloudTrail and configure KMS encryption"
            )
        
        all_details = []
        kms_encrypted_trails = []
        unencrypted_trails = []
        
        for trail in trails:
            kms_key_id = trail.get('KmsKeyId')
            
            trail_info = {
                "trail_name": trail.get('Name'),
                "arn": trail.get('TrailARN'),
                "kms_key_id": kms_key_id,
                "is_cmk": is_customer_managed_key(kms_key_id) if kms_key_id else False
            }
            all_details.append(trail_info)
            
            if kms_key_id and is_customer_managed_key(kms_key_id):
                kms_encrypted_trails.append(trail.get('Name'))
            else:
                unencrypted_trails.append(trail.get('Name'))
        
        if unencrypted_trails:
            status = 'FAIL'
            details = {
                "kms_encrypted_trails": kms_encrypted_trails,
                "unencrypted_trails": unencrypted_trails,
                "all_trails": all_details
            }
        else:
            status = 'PASS'
            details = {
                "kms_encrypted_trails": kms_encrypted_trails,
                "all_trails": all_details
            }
        
        return create_result(
            control_id,
            control['title'],
            status,
            control['severity'],
            details=details,
            resource_id=','.join(kms_encrypted_trails) if kms_encrypted_trails else None,
            remediation="Enable KMS CMK encryption for CloudTrail logs" if status == 'FAIL' else None
        )
    
    except Exception as e:
        logger.error(f"Error checking control 3.4: {str(e)}")
        return create_result(
            control_id,
            control['title'],
            'UNKNOWN',
            control['severity'],
            details={"error": str(e)}
        )
