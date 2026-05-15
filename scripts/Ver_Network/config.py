"""
AWS configuration helpers for the network benchmark.
"""
import logging

try:
    import boto3
except ImportError:  # pragma: no cover - handled at runtime with a clear error
    boto3 = None

try:
    from botocore.exceptions import ClientError
except ImportError:  # pragma: no cover - handled at runtime with a clear error
    ClientError = Exception

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_clients = {}


def get_aws_session(profile_name=None, region_name=None):
    """Create a boto3 session."""
    if boto3 is None:
        raise RuntimeError("boto3 is required to run the network benchmark")
    return boto3.Session(profile_name=profile_name, region_name=region_name)


def get_client(service_name, region_name=None, profile_name=None):
    """Return a cached boto3 client."""
    cache_key = f"{service_name}_{region_name}_{profile_name}"

    if cache_key not in _clients:
        session = get_aws_session(profile_name=profile_name, region_name=region_name)
        _clients[cache_key] = session.client(service_name, region_name=region_name)

    return _clients[cache_key]


def get_all_regions(profile_name=None):
    """Return all enabled AWS regions in the account."""
    try:
        ec2_client = get_client("ec2", profile_name=profile_name)
        response = ec2_client.describe_regions(AllRegions=False)
        return [region["RegionName"] for region in response.get("Regions", [])]
    except ClientError as error:
        logger.error(f"Failed to get regions: {error}")
        return []


def get_account_id(profile_name=None):
    """Return the AWS account ID."""
    try:
        sts_client = get_client("sts", profile_name=profile_name)
        response = sts_client.get_caller_identity()
        return response["Account"]
    except ClientError as error:
        logger.error(f"Failed to get account ID: {error}")
        return None


def get_project_vpcs(profile_name=None, regions=None, project_name="cis-baseline", environment="dev"):
    """Return VPCs that match the project tags across the selected regions."""
    regions = regions or get_all_regions(profile_name=profile_name)
    vpcs = []

    for region in regions:
        ec2_client = get_client("ec2", region_name=region, profile_name=profile_name)
        response = ec2_client.describe_vpcs(
            Filters=[
                {"Name": "tag:Project", "Values": [project_name]},
                {"Name": "tag:Environment", "Values": [environment]},
            ]
        )
        for vpc in response.get("Vpcs", []):
            vpcs.append({"region": region, **vpc})

    return vpcs


def get_project_subnets(profile_name=None, regions=None, project_name="cis-baseline", environment="dev", subnet_type=None):
    """Return subnets that match the project tags across the selected regions."""
    regions = regions or get_all_regions(profile_name=profile_name)
    subnets = []

    for region in regions:
        ec2_client = get_client("ec2", region_name=region, profile_name=profile_name)
        filters = [
            {"Name": "tag:Project", "Values": [project_name]},
            {"Name": "tag:Environment", "Values": [environment]},
        ]
        if subnet_type:
            filters.append({"Name": "tag:Type", "Values": [subnet_type]})

        response = ec2_client.describe_subnets(Filters=filters)
        for subnet in response.get("Subnets", []):
            subnets.append({"region": region, **subnet})

    return subnets


NETWORK_CONTROLS = {
    "6.1.1": {
        "title": "Ensure EBS volume encryption is enabled in all regions",
        "severity": "HIGH",
        "category": "EC2",
    },
    "6.1.2": {
        "title": "Ensure CIFS access is restricted to trusted networks to prevent unauthorized access",
        "severity": "HIGH",
        "category": "EC2",
    },
    "6.2": {
        "title": "Ensure no Network ACLs allow ingress from 0.0.0.0/0 to remote server administration ports",
        "severity": "HIGH",
        "category": "Network ACL",
    },
    "6.3": {
        "title": "Ensure no security groups allow ingress from 0.0.0.0/0 to remote server administration ports",
        "severity": "HIGH",
        "category": "Security Group",
    },
    "6.4": {
        "title": "Ensure no security groups allow ingress from ::/0 to remote server administration ports",
        "severity": "HIGH",
        "category": "Security Group",
    },
    "6.5": {
        "title": "Ensure the default security group of every VPC restricts all traffic",
        "severity": "CRITICAL",
        "category": "Security Group",
    },
    "6.6": {
        "title": "Ensure routing tables for VPC peering are least access",
        "severity": "MEDIUM",
        "category": "Routing",
    },
    "6.7": {
        "title": "Ensure that the EC2 Metadata Service only allows IMDSv2",
        "severity": "HIGH",
        "category": "EC2",
    },
}
