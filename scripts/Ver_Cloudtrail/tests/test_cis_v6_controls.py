import inspect
import unittest

from scripts.Ver_Cloudtrail import config
from scripts.Ver_Cloudtrail.benchmark_checker import CONTROLS, normalize_control_id
from scripts.Ver_Cloudtrail.checks.common import event_selectors_have_s3_logging
from scripts.Ver_Cloudtrail.checks.control_4_6 import _is_customer_created_symmetric_key


class CisV6ControlTests(unittest.TestCase):
    def test_checker_maps_to_cis_v6_logging_controls(self):
        self.assertEqual(list(sorted(CONTROLS.keys())), [f"4.{index}" for index in range(1, 10)])
        self.assertEqual(list(sorted(config.CIS_CONTROLS.keys())), [f"4.{index}" for index in range(1, 10)])

    def test_old_control_numbers_are_accepted_as_aliases(self):
        self.assertEqual(normalize_control_id("3.1"), "4.1")
        self.assertEqual(normalize_control_id("3.9"), "4.9")
        self.assertEqual(normalize_control_id("4.7"), "4.7")

    def test_get_aws_session_accepts_region_name_used_by_get_client(self):
        signature = inspect.signature(config.get_aws_session)
        self.assertIn("region_name", signature.parameters)

    def test_classic_s3_event_selector_uses_read_write_type_from_selector(self):
        response = {
            "EventSelectors": [
                {
                    "ReadWriteType": "WriteOnly",
                    "DataResources": [
                        {"Type": "AWS::S3::Object", "Values": ["arn:aws:s3:::example-bucket/"]}
                    ],
                }
            ]
        }

        self.assertTrue(event_selectors_have_s3_logging(response, "write"))
        self.assertFalse(event_selectors_have_s3_logging(response, "read"))

    def test_advanced_s3_event_selector_supports_read_and_write_filters(self):
        write_response = {
            "AdvancedEventSelectors": [
                {
                    "FieldSelectors": [
                        {"Field": "eventCategory", "Equals": ["Data"]},
                        {"Field": "resources.type", "Equals": ["AWS::S3::Object"]},
                        {"Field": "readOnly", "Equals": ["false"]},
                    ]
                }
            ]
        }
        read_response = {
            "AdvancedEventSelectors": [
                {
                    "FieldSelectors": [
                        {"Field": "eventCategory", "Equals": ["Data"]},
                        {"Field": "resources.type", "Equals": ["AWS::S3::Object"]},
                        {"Field": "readOnly", "Equals": ["true"]},
                    ]
                }
            ]
        }

        self.assertTrue(event_selectors_have_s3_logging(write_response, "write"))
        self.assertFalse(event_selectors_have_s3_logging(write_response, "read"))
        self.assertTrue(event_selectors_have_s3_logging(read_response, "read"))
        self.assertFalse(event_selectors_have_s3_logging(read_response, "write"))

    def test_advanced_selector_does_not_treat_negative_resource_filters_as_s3_logging(self):
        response = {
            "AdvancedEventSelectors": [
                {
                    "FieldSelectors": [
                        {"Field": "eventCategory", "Equals": ["Data"]},
                        {"Field": "resources.type", "NotEquals": ["AWS::S3::Object"]},
                    ]
                }
            ]
        }

        self.assertFalse(event_selectors_have_s3_logging(response, "write"))
        self.assertFalse(event_selectors_have_s3_logging(response, "read"))

    def test_kms_rotation_scope_is_customer_created_symmetric_keys(self):
        self.assertTrue(
            _is_customer_created_symmetric_key(
                {"KeyManager": "CUSTOMER", "KeySpec": "SYMMETRIC_DEFAULT", "KeyState": "Enabled"}
            )
        )
        self.assertFalse(
            _is_customer_created_symmetric_key(
                {"KeyManager": "AWS", "KeySpec": "SYMMETRIC_DEFAULT", "KeyState": "Enabled"}
            )
        )
        self.assertFalse(
            _is_customer_created_symmetric_key(
                {"KeyManager": "CUSTOMER", "KeySpec": "RSA_2048", "KeyState": "Enabled"}
            )
        )


if __name__ == "__main__":
    unittest.main()
