"""
CIS 4.6: Ensure rotation for customer-created symmetric CMKs is enabled.
"""
import logging

from scripts.Ver_Cloudtrail.config import CIS_CONTROLS, get_all_regions, get_client
from scripts.Ver_Cloudtrail.utils import create_result, error_handler

logger = logging.getLogger(__name__)


def _is_customer_created_symmetric_key(metadata):
    return (
        metadata.get("KeyManager") == "CUSTOMER"
        and metadata.get("KeySpec") == "SYMMETRIC_DEFAULT"
        and metadata.get("KeyState") == "Enabled"
    )


@error_handler
def check_control_4_6(profile_name=None, regions=None):
    control_id = "4.6"
    control = CIS_CONTROLS[control_id]
    if not regions:
        regions = get_all_regions(profile_name=profile_name)

    all_details = []
    rotation_enabled = []
    rotation_disabled = []

    for region in regions:
        try:
            kms_client = get_client("kms", region_name=region, profile_name=profile_name)
            paginator = kms_client.get_paginator("list_keys")
            for page in paginator.paginate():
                for key in page.get("Keys", []):
                    key_id = key.get("KeyId")
                    try:
                        metadata = kms_client.describe_key(KeyId=key_id).get("KeyMetadata", {})
                        if not _is_customer_created_symmetric_key(metadata):
                            continue

                        rotation = kms_client.get_key_rotation_status(KeyId=key_id).get(
                            "KeyRotationEnabled", False
                        )
                        key_info = {
                            "region": region,
                            "key_id": key_id,
                            "arn": metadata.get("Arn"),
                            "rotation_enabled": rotation,
                        }
                        all_details.append(key_info)
                        if rotation:
                            rotation_enabled.append(metadata.get("Arn") or key_id)
                        else:
                            rotation_disabled.append(metadata.get("Arn") or key_id)
                    except Exception as exc:
                        logger.warning("Could not inspect KMS key %s in %s: %s", key_id, region, exc)
                        all_details.append({"region": region, "key_id": key_id, "error": str(exc)})
                        rotation_disabled.append(key_id)
        except Exception as exc:
            logger.warning("Could not list KMS keys in %s: %s", region, exc)
            all_details.append({"region": region, "error": str(exc)})

    status = "PASS" if not rotation_disabled else "FAIL"
    return create_result(
        control_id,
        control["title"],
        status,
        control["severity"],
        details={
            "rotation_enabled_keys": rotation_enabled,
            "rotation_disabled_keys": rotation_disabled,
            "all_customer_created_symmetric_keys": all_details,
        },
        resource_id=",".join(rotation_enabled) if rotation_enabled else None,
        remediation="Enable automatic rotation on every enabled customer-created symmetric KMS key" if status == "FAIL" else None,
    )
