"""
Shared helpers for CIS AWS Foundations Benchmark v6 logging checks.
"""
import logging

from scripts.Ver_Cloudtrail.config import get_all_regions, get_client

logger = logging.getLogger(__name__)


def discover_trails(profile_name=None, regions=None):
    """
    Return unique CloudTrail trails visible across the selected regions.

    Using includeShadowTrails=True and de-duplicating by ARN lets controls find
    trails whose home region differs from the default boto3 region.
    """
    if not regions:
        regions = get_all_regions(profile_name=profile_name)

    trails_by_arn = {}
    errors = []

    for region in regions:
        try:
            client = get_client("cloudtrail", region_name=region, profile_name=profile_name)
            response = client.describe_trails(includeShadowTrails=True)
            for trail in response.get("trailList", []):
                trail_arn = trail.get("TrailARN") or trail.get("Name")
                if not trail_arn:
                    continue
                existing = trails_by_arn.get(trail_arn, {})
                merged = {**existing, **trail}
                merged.setdefault("DiscoveredRegions", set())
                merged["DiscoveredRegions"].add(region)
                trails_by_arn[trail_arn] = merged
        except Exception as exc:
            logger.warning("Could not describe CloudTrail trails in %s: %s", region, exc)
            errors.append({"region": region, "error": str(exc)})

    trails = []
    for trail in trails_by_arn.values():
        discovered_regions = trail.get("DiscoveredRegions", set())
        trail["DiscoveredRegions"] = sorted(discovered_regions)
        trails.append(trail)

    return trails, errors


def get_trail_status(trail, profile_name=None):
    """Return CloudTrail status, using the trail home region when available."""
    region = trail.get("HomeRegion") or (trail.get("DiscoveredRegions") or [None])[0]
    client = get_client("cloudtrail", region_name=region, profile_name=profile_name)
    return client.get_trail_status(Name=trail.get("TrailARN") or trail.get("Name"))


def is_customer_managed_kms_key_id(key_id):
    """CloudTrail KMS encryption should use a customer managed KMS key ARN."""
    if not key_id:
        return False
    return ":kms:" in key_id and ":key/" in key_id


def regular_selector_has_s3_logging(selector, event_kind):
    """
    Check classic CloudTrail event selectors for S3 object data events.

    ReadWriteType belongs to the event selector, not the DataResources Values.
    Values contain resource ARN prefixes.
    """
    read_write_type = selector.get("ReadWriteType", "All")
    if event_kind == "write":
        allowed_types = {"WriteOnly", "All"}
    else:
        allowed_types = {"ReadOnly", "All"}

    if read_write_type not in allowed_types:
        return False

    return any(
        resource.get("Type") == "AWS::S3::Object"
        for resource in selector.get("DataResources", [])
    )


def _positive_field_values(field_selector):
    values = set()
    for key in ("Equals", "StartsWith", "EndsWith"):
        values.update(str(value) for value in field_selector.get(key, []))
    return values


def _negative_field_values(field_selector):
    values = set()
    for key in ("NotEquals", "NotStartsWith", "NotEndsWith"):
        values.update(str(value) for value in field_selector.get(key, []))
    return values


def advanced_selector_has_s3_logging(selector, event_kind):
    """
    Check CloudTrail advanced event selectors for S3 object data events.

    If readOnly is absent, the selector covers both read and write events.
    """
    fields = selector.get("FieldSelectors", [])
    positive_by_field = {field.get("Field"): _positive_field_values(field) for field in fields}
    negative_by_field = {field.get("Field"): _negative_field_values(field) for field in fields}

    event_categories = positive_by_field.get("eventCategory", set())
    if event_categories and "Data" not in event_categories:
        return False

    resource_types = positive_by_field.get("resources.type", set())
    if "AWS::S3::Object" not in resource_types:
        return False

    read_only_values = {value.lower() for value in positive_by_field.get("readOnly", set())}
    if not read_only_values:
        not_read_only_values = {value.lower() for value in negative_by_field.get("readOnly", set())}
        if event_kind == "write" and "true" in not_read_only_values:
            return True
        if event_kind == "read" and "false" in not_read_only_values:
            return True
        return not not_read_only_values

    if event_kind == "write":
        return "false" in read_only_values
    return "true" in read_only_values


def event_selectors_have_s3_logging(response, event_kind):
    """Return True when classic or advanced selectors include S3 read/write data events."""
    return any(
        regular_selector_has_s3_logging(selector, event_kind)
        for selector in response.get("EventSelectors", [])
    ) or any(
        advanced_selector_has_s3_logging(selector, event_kind)
        for selector in response.get("AdvancedEventSelectors", [])
    )
