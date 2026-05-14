"""
AWS configuration and CIS control metadata for monitoring benchmark.
"""
import logging

import boto3
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_clients = {}


def get_aws_session(profile_name=None, region=None):
  return boto3.Session(profile_name=profile_name, region_name=region)


def get_client(service_name, region_name=None, profile_name=None):
  cache_key = f"{service_name}_{region_name}_{profile_name}"
  if cache_key not in _clients:
    session = get_aws_session(profile_name=profile_name, region=region_name)
    _clients[cache_key] = session.client(service_name, region_name=region_name)
  return _clients[cache_key]


def get_all_regions(profile_name=None):
  try:
    ec2_client = get_client("ec2", profile_name=profile_name)
    response = ec2_client.describe_regions(AllRegions=False)
    return [region["RegionName"] for region in response["Regions"]]
  except ClientError as error:
    logger.error("Failed to discover regions: %s", error)
    return []


def get_account_id(profile_name=None):
  try:
    sts_client = get_client("sts", profile_name=profile_name)
    response = sts_client.get_caller_identity()
    return response["Account"]
  except ClientError as error:
    logger.error("Failed to get account id: %s", error)
    return None


CIS_CONTROLS = {
  "5.1": {
    "title": "Ensure unauthorized API calls are monitored",
    "severity": "CRITICAL",
    "metric_name": "UnauthorizedAPICalls",
  },
  "5.2": {
    "title": "Ensure management console sign-in without MFA is monitored",
    "severity": "HIGH",
    "metric_name": "ConsoleSigninWithoutMFA",
  },
  "5.3": {
    "title": "Ensure usage of the 'root' account is monitored",
    "severity": "HIGH",
    "metric_name": "RootAccountUsage",
  },
  "5.4": {
    "title": "Ensure IAM policy changes are monitored",
    "severity": "HIGH",
    "metric_name": "IAMPolicyChanges",
  },
  "5.5": {
    "title": "Ensure CloudTrail configuration changes are monitored",
    "severity": "HIGH",
    "metric_name": "CloudTrailConfigChanges",
  },
}
