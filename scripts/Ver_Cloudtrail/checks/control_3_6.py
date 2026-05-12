"""
CIS 3.6: Ensure AWS Config is enabled in all regions
"""
import logging
from scripts.Ver_Cloudtrail.config import get_client, get_all_regions, CIS_CONTROLS
from scripts.Ver_Cloudtrail.utils import create_result, error_handler

logger = logging.getLogger(__name__)

@error_handler
def check_control_3_6(profile_name=None, regions=None):
    """
    Check if AWS Config is enabled in all regions
    
    Verifies:
    - Config recorder exists in each region
    - Recording = true
    - lastStatus = SUCCESS
    - Delivery channel configured
    - Global resources captured in at least one region
    
    Args:
        profile_name: AWS profile name
        regions: List of regions to check (if None, checks all regions)
    
    Returns:
        dict with control result
    """
    control_id = "3.6"
    control = CIS_CONTROLS[control_id]
    
    try:
        # Get all regions if not specified
        if not regions:
            regions = get_all_regions(profile_name=profile_name)
        
        all_details = []
        config_enabled_regions = []
        config_disabled_regions = []
        global_resources_regions = []
        
        for region in regions:
            try:
                config_client = get_client('config', region_name=region, profile_name=profile_name)
                
                # Get recorders
                recorders_response = config_client.describe_configuration_recorders()
                recorders = recorders_response.get('ConfigurationRecorders', [])
                
                if not recorders:
                    region_info = {
                        "region": region,
                        "config_enabled": False,
                        "reason": "No recorder found"
                    }
                    all_details.append(region_info)
                    config_disabled_regions.append(region)
                    continue
                
                # Check recorder status
                recorder = recorders[0]
                recorder_name = recorder.get('name')
                
                try:
                    status_response = config_client.describe_configuration_recorder_status(
                        ConfigurationRecorderNames=[recorder_name]
                    )
                    recorder_status = status_response.get('ConfigurationRecordersStatus', [{}])[0]
                    recording = recorder_status.get('recording', False)
                    last_status = recorder_status.get('lastStatus', 'UNKNOWN')
                except Exception as e:
                    logger.warning(f"Could not get recorder status in {region}: {str(e)}")
                    recording = False
                    last_status = 'UNKNOWN'
                
                # Check if recording all resources
                recording_group = recorder.get('recordingGroup', {})
                recording_all = recording_group.get('allSupported', False)
                include_global = recording_group.get('includeGlobalResources', False)
                
                region_info = {
                    "region": region,
                    "config_enabled": recording and last_status == 'SUCCESS',
                    "recording": recording,
                    "last_status": last_status,
                    "recording_all": recording_all,
                    "include_global_resources": include_global
                }
                all_details.append(region_info)
                
                if recording and last_status == 'SUCCESS':
                    config_enabled_regions.append(region)
                    if include_global:
                        global_resources_regions.append(region)
                else:
                    config_disabled_regions.append(region)
            
            except Exception as e:
                logger.warning(f"Error checking Config in region {region}: {str(e)}")
                region_info = {
                    "region": region,
                    "error": str(e)
                }
                all_details.append(region_info)
                config_disabled_regions.append(region)
        
        # Determine overall status
        if not config_enabled_regions:
            status = 'FAIL'
            details = {
                "reason": "AWS Config not enabled in any region",
                "config_enabled_regions": config_enabled_regions,
                "config_disabled_regions": config_disabled_regions,
                "by_region": all_details
            }
        elif not global_resources_regions:
            status = 'FAIL'
            details = {
                "reason": "Global resources not being recorded",
                "config_enabled_regions": config_enabled_regions,
                "global_resources_regions": global_resources_regions,
                "by_region": all_details
            }
        else:
            status = 'PASS'
            details = {
                "config_enabled_regions": config_enabled_regions,
                "global_resources_regions": global_resources_regions,
                "by_region": all_details
            }
        
        return create_result(
            control_id,
            control['title'],
            status,
            control['severity'],
            details=details,
            resource_id=','.join(config_enabled_regions) if config_enabled_regions else None,
            remediation="Enable AWS Config in all regions with global resources recording" if status == 'FAIL' else None
        )
    
    except Exception as e:
        logger.error(f"Error checking control 3.6: {str(e)}")
        return create_result(
            control_id,
            control['title'],
            'UNKNOWN',
            control['severity'],
            details={"error": str(e)}
        )
