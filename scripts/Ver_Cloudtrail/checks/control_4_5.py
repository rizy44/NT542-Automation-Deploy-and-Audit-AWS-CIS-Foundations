"""
CIS 4.5: Ensure CloudTrail logs are encrypted at rest using KMS CMKs.
"""
from scripts.Ver_Cloudtrail.config import CIS_CONTROLS
from scripts.Ver_Cloudtrail.checks.common import discover_trails, is_customer_managed_kms_key_id
from scripts.Ver_Cloudtrail.utils import create_result, error_handler


@error_handler
def check_control_4_5(profile_name=None, regions=None):
    control_id = "4.5"
    control = CIS_CONTROLS[control_id]
    trails, discovery_errors = discover_trails(profile_name=profile_name, regions=regions)
    if not trails:
        return create_result(
            control_id,
            control["title"],
            "FAIL",
            control["severity"],
            details={"reason": "No CloudTrail trails found", "discovery_errors": discovery_errors},
            remediation="Enable CloudTrail and configure KMS encryption with a customer managed key",
        )

    encrypted = []
    unencrypted = []
    all_details = []

    for trail in trails:
        kms_key_id = trail.get("KmsKeyId")
        compliant = is_customer_managed_kms_key_id(kms_key_id)
        all_details.append(
            {
                "trail_name": trail.get("Name"),
                "arn": trail.get("TrailARN"),
                "kms_key_id": kms_key_id,
                "uses_customer_managed_kms_key": compliant,
            }
        )
        if compliant:
            encrypted.append(trail.get("Name"))
        else:
            unencrypted.append(trail.get("Name"))

    status = "PASS" if not unencrypted else "FAIL"
    return create_result(
        control_id,
        control["title"],
        status,
        control["severity"],
        details={
            "kms_encrypted_trails": encrypted,
            "unencrypted_trails": unencrypted,
            "all_trails": all_details,
            "discovery_errors": discovery_errors,
        },
        resource_id=",".join(encrypted) if encrypted else None,
        remediation="Configure every CloudTrail trail to encrypt logs with a customer managed KMS key" if status == "FAIL" else None,
    )
