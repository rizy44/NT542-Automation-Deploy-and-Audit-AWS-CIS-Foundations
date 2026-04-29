"""
CIS 3.5: Ensure KMS key rotation is enabled
"""
import logging
from config import get_client, CIS_CONTROLS
from utils import create_result, error_handler

logger = logging.getLogger(__name__)

@error_handler
def check_control_3_5(profile_name=None, regions=None):
    """
    Check if KMS key rotation is enabled for CloudTrail keys
    
    Verifies:
    - KeyRotationEnabled = true for each KMS key used by CloudTrail
    
    Args:
        profile_name: AWS profile name
        regions: List of regions to check (if None, checks all regions)
    
    Returns:
        dict with control result
    """
    control_id = "3.5"
    control = CIS_CONTROLS[control_id]
    
    try:
        cloudtrail_client = get_client('cloudtrail', profile_name=profile_name)
        
        # Describe trails to get KMS keys
        response = cloudtrail_client.describe_trails(includeShadowTrails=False)
        trails = response.get('trailList', [])
        
        if not trails:
            return create_result(
                control_id,
                control['title'],
                'FAIL',
                control['severity'],
                details={"reason": "No CloudTrail trails found"},
                remediation="Enable CloudTrail with KMS encryption and enable key rotation"
            )
        
        # Collect unique KMS key IDs
        kms_key_ids = set()
        for trail in trails:
            kms_key_id = trail.get('KmsKeyId')
            if kms_key_id and kms_key_id.startswith('arn:aws:kms:'):
                kms_key_ids.add(kms_key_id)
        
        if not kms_key_ids:
            return create_result(
                control_id,
                control['title'],
                'FAIL',
                control['severity'],
                details={"reason": "No KMS CMK keys found for CloudTrail"},
                remediation="Enable KMS CMK encryption with automatic key rotation"
            )
        
        all_details = []
        rotation_enabled_keys = []
        rotation_disabled_keys = []
        
        for kms_key_id in kms_key_ids:
            # Extract region from ARN
            try:
                region = kms_key_id.split(':')[3]
                kms_client = get_client('kms', region_name=region, profile_name=profile_name)
                
                # Get key rotation status
                rotation_response = kms_client.get_key_rotation_status(KeyId=kms_key_id)
                rotation_enabled = rotation_response.get('KeyRotationEnabled', False)
                
                key_info = {
                    "key_id": kms_key_id,
                    "region": region,
                    "rotation_enabled": rotation_enabled
                }
                all_details.append(key_info)
                
                if rotation_enabled:
                    rotation_enabled_keys.append(kms_key_id)
                else:
                    rotation_disabled_keys.append(kms_key_id)
            
            except Exception as e:
                logger.warning(f"Could not check rotation for key {kms_key_id}: {str(e)}")
                key_info = {
                    "key_id": kms_key_id,
                    "error": str(e)
                }
                all_details.append(key_info)
                rotation_disabled_keys.append(kms_key_id)
        
        if rotation_disabled_keys:
            status = 'FAIL'
            details = {
                "rotation_enabled_keys": rotation_enabled_keys,
                "rotation_disabled_keys": rotation_disabled_keys,
                "all_keys": all_details
            }
        else:
            status = 'PASS'
            details = {
                "rotation_enabled_keys": rotation_enabled_keys,
                "all_keys": all_details
            }
        
        return create_result(
            control_id,
            control['title'],
            status,
            control['severity'],
            details=details,
            resource_id=','.join(rotation_enabled_keys) if rotation_enabled_keys else None,
            remediation="Enable automatic key rotation for all KMS keys" if status == 'FAIL' else None
        )
    
    except Exception as e:
        logger.error(f"Error checking control 3.5: {str(e)}")
        return create_result(
            control_id,
            control['title'],
            'UNKNOWN',
            control['severity'],
            details={"error": str(e)}
        )
