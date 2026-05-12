"""
AWS Configuration Module
Handles AWS session, client initialization, and region discovery
"""
import boto3
from botocore.exceptions import BotoCoreError, ClientError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AWS clients cache
_clients = {}

def get_aws_session(profile_name=None, region=None):
    """
    Initialize AWS session
    
    Args:
        profile_name: AWS profile name (optional)
        region: AWS region (optional)
    
    Returns:
        boto3.Session
    """
    try:
        session = boto3.Session(profile_name=profile_name, region_name=region)
        return session
    except Exception as e:
        logger.error(f"Failed to create AWS session: {str(e)}")
        raise

def get_client(service_name, region_name=None, profile_name=None):
    """
    Get or create AWS service client
    
    Args:
        service_name: AWS service (e.g., 'cloudtrail', 's3', 'ec2')
        region_name: AWS region
        profile_name: AWS profile name
    
    Returns:
        boto3 client
    """
    cache_key = f"{service_name}_{region_name}_{profile_name}"
    
    if cache_key not in _clients:
        try:
            session = get_aws_session(profile_name=profile_name, region_name=region_name)
            _clients[cache_key] = session.client(service_name, region_name=region_name)
        except Exception as e:
            logger.error(f"Failed to create client for {service_name}: {str(e)}")
            raise
    
    return _clients[cache_key]

def get_all_regions(profile_name=None):
    """
    Get all AWS regions
    
    Args:
        profile_name: AWS profile name
    
    Returns:
        List of region names
    """
    try:
        ec2_client = get_client('ec2', profile_name=profile_name)
        response = ec2_client.describe_regions(AllRegions=False)
        regions = [region['RegionName'] for region in response['Regions']]
        logger.info(f"Discovered {len(regions)} regions")
        return regions
    except ClientError as e:
        logger.error(f"Failed to get regions: {str(e)}")
        return []

def get_account_id(profile_name=None):
    """
    Get AWS account ID
    
    Args:
        profile_name: AWS profile name
    
    Returns:
        AWS account ID as string
    """
    try:
        sts_client = get_client('sts', profile_name=profile_name)
        response = sts_client.get_caller_identity()
        return response['Account']
    except ClientError as e:
        logger.error(f"Failed to get account ID: {str(e)}")
        return None

# CIS Control Definitions
CIS_CONTROLS = {
    "3.1": {
        "title": "Ensure CloudTrail is enabled in all regions",
        "severity": "CRITICAL",
        "category": "CloudTrail"
    },
    "3.2": {
        "title": "Ensure log file validation is enabled",
        "severity": "HIGH",
        "category": "CloudTrail"
    },
    "3.3": {
        "title": "Ensure S3 bucket access logging is enabled",
        "severity": "HIGH",
        "category": "CloudTrail"
    },
    "3.4": {
        "title": "Ensure CloudTrail logs are encrypted with KMS CMK",
        "severity": "HIGH",
        "category": "CloudTrail"
    },
    "3.5": {
        "title": "Ensure KMS key rotation is enabled",
        "severity": "MEDIUM",
        "category": "KMS"
    },
    "3.6": {
        "title": "Ensure AWS Config is enabled in all regions",
        "severity": "HIGH",
        "category": "Config"
    },
    "3.7": {
        "title": "Ensure VPC Flow Logs are enabled",
        "severity": "HIGH",
        "category": "VPC"
    },
    "3.8": {
        "title": "Ensure S3 object-level logging for WRITE events",
        "severity": "MEDIUM",
        "category": "CloudTrail"
    },
    "3.9": {
        "title": "Ensure S3 object-level logging for READ events",
        "severity": "MEDIUM",
        "category": "CloudTrail"
    }
}
