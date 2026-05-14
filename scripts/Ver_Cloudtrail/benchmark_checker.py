#!/usr/bin/env python3
"""
CIS AWS Foundations Benchmark v6 logging checker.
"""
import argparse
import logging
import sys
from pathlib import Path

# Make imports work whether this script is launched from the repo root or from
# scripts/Ver_Cloudtrail.
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from scripts.Ver_Cloudtrail.config import get_account_id, get_all_regions
from scripts.Ver_Cloudtrail.utils import BenchmarkReport, print_report_summary

from scripts.Ver_Cloudtrail.checks.control_4_1 import check_control_4_1
from scripts.Ver_Cloudtrail.checks.control_4_2 import check_control_4_2
from scripts.Ver_Cloudtrail.checks.control_4_3 import check_control_4_3
from scripts.Ver_Cloudtrail.checks.control_4_4 import check_control_4_4
from scripts.Ver_Cloudtrail.checks.control_4_5 import check_control_4_5
from scripts.Ver_Cloudtrail.checks.control_4_6 import check_control_4_6
from scripts.Ver_Cloudtrail.checks.control_4_7 import check_control_4_7
from scripts.Ver_Cloudtrail.checks.control_4_8 import check_control_4_8
from scripts.Ver_Cloudtrail.checks.control_4_9 import check_control_4_9

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

CONTROLS = {
    "4.1": check_control_4_1,
    "4.2": check_control_4_2,
    "4.3": check_control_4_3,
    "4.4": check_control_4_4,
    "4.5": check_control_4_5,
    "4.6": check_control_4_6,
    "4.7": check_control_4_7,
    "4.8": check_control_4_8,
    "4.9": check_control_4_9,
}

LEGACY_CONTROL_ALIASES = {f"3.{index}": f"4.{index}" for index in range(1, 10)}


def normalize_control_id(control_id):
    """Accept old 3.x control input while running CIS v6 4.x controls."""
    control_id = control_id.strip()
    return LEGACY_CONTROL_ALIASES.get(control_id, control_id)


class BenchmarkChecker:
    """Run CIS AWS Foundations Benchmark v6 logging checks."""

    def __init__(self, profile_name=None, regions=None, verbose=False):
        self.profile_name = profile_name
        self.regions = regions
        self.verbose = verbose

        if verbose:
            logging.getLogger().setLevel(logging.DEBUG)

    def _prepare_report(self):
        account_id = get_account_id(profile_name=self.profile_name)
        if not account_id:
            logger.error("Could not retrieve AWS account ID. Please check your credentials.")
            return None

        logger.info("Account ID: %s", account_id)

        if not self.regions:
            logger.info("Discovering AWS regions...")
            self.regions = get_all_regions(profile_name=self.profile_name)

        logger.info("Checking %s regions: %s", len(self.regions), ", ".join(self.regions))
        return BenchmarkReport(account_id, self.regions)

    def run_all_checks(self):
        """Run all CIS 4.1-4.9 controls."""
        logger.info("Starting CIS AWS Foundations Benchmark v6 logging checks...")
        report = self._prepare_report()
        if not report:
            return None

        for control_id in sorted(CONTROLS.keys()):
            self._run_control(report, control_id)

        logger.info("All checks completed.")
        return report

    def run_specific_controls(self, control_ids):
        """Run selected CIS controls."""
        normalized_control_ids = [normalize_control_id(control_id) for control_id in control_ids]
        logger.info("Running specific controls: %s", ", ".join(normalized_control_ids))

        report = self._prepare_report()
        if not report:
            return None

        for control_id in normalized_control_ids:
            self._run_control(report, control_id)

        logger.info("Selected checks completed.")
        return report

    def _run_control(self, report, control_id):
        if control_id not in CONTROLS:
            logger.warning("Control CIS %s not found", control_id)
            return

        logger.info("Running check for CIS %s...", control_id)
        try:
            result = CONTROLS[control_id](
                profile_name=self.profile_name,
                regions=self.regions,
            )

            if result:
                report.add_result(result)
                status_marker = "PASS" if result["status"] == "PASS" else result["status"]
                logger.info("  CIS %s: %s", control_id, status_marker)
            else:
                logger.warning("  No result returned for CIS %s", control_id)
        except Exception as exc:
            logger.error("Error running check CIS %s: %s", control_id, exc)


def main():
    parser = argparse.ArgumentParser(
        description="CIS AWS Foundations Benchmark v6 Logging Checker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all checks
  python benchmark_checker.py

  # Run all checks with verbose output
  python benchmark_checker.py -v

  # Run specific controls
  python benchmark_checker.py --controls 4.1,4.2,4.3

  # Backward-compatible old numbering is accepted
  python benchmark_checker.py --controls 3.1,3.2,3.3

  # Run all checks and save to file
  python benchmark_checker.py --output report.json

  # Run with specific AWS profile and regions
  python benchmark_checker.py --profile prod --regions us-east-1,eu-west-1
        """,
    )

    parser.add_argument(
        "--controls",
        help="Specific controls to check (comma-separated, e.g., 4.1,4.2)",
        default=None,
    )
    parser.add_argument(
        "--regions",
        help="Specific regions to check (comma-separated)",
        default=None,
    )
    parser.add_argument(
        "--profile",
        help="AWS profile name",
        default=None,
    )
    parser.add_argument(
        "--output",
        help="Output file path for JSON report",
        default=None,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose output",
    )

    args = parser.parse_args()

    regions = None
    if args.regions:
        regions = [region.strip() for region in args.regions.split(",")]

    checker = BenchmarkChecker(
        profile_name=args.profile,
        regions=regions,
        verbose=args.verbose,
    )

    if args.controls:
        control_ids = [normalize_control_id(control_id) for control_id in args.controls.split(",")]
        report = checker.run_specific_controls(control_ids)
    else:
        report = checker.run_all_checks()

    if not report:
        logger.error("Failed to generate report")
        sys.exit(1)

    print_report_summary(report)

    if args.output:
        logger.info("Saving report to %s", args.output)
        if report.save_to_file(args.output):
            logger.info("Report successfully saved to %s", args.output)
        else:
            logger.error("Failed to save report")
            sys.exit(1)

    print("\n" + "=" * 60)
    print("Full JSON Report:")
    print("=" * 60)
    print(report.to_json(pretty=True))

    summary = report.get_summary()
    sys.exit(1 if summary["failed"] > 0 else 0)


if __name__ == "__main__":
    main()
