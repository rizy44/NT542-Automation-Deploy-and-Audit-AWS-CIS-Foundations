#!/usr/bin/env python3
"""
Network benchmark checker for the lab infrastructure.
"""
import argparse
import logging
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from scripts.Ver_Network.checks.control_6_1_1 import check_control_6_1_1
from scripts.Ver_Network.checks.control_6_1_2 import check_control_6_1_2
from scripts.Ver_Network.checks.control_6_2 import check_control_6_2
from scripts.Ver_Network.checks.control_6_3 import check_control_6_3
from scripts.Ver_Network.checks.control_6_4 import check_control_6_4
from scripts.Ver_Network.checks.control_6_5 import check_control_6_5
from scripts.Ver_Network.checks.control_6_6 import check_control_6_6
from scripts.Ver_Network.checks.control_6_7 import check_control_6_7
from scripts.Ver_Network.config import get_account_id, get_all_regions
from scripts.Ver_Network.utils import BenchmarkReport, print_report_summary

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

CONTROLS = {
    "6.1.1": check_control_6_1_1,
    "6.1.2": check_control_6_1_2,
    "6.2": check_control_6_2,
    "6.3": check_control_6_3,
    "6.4": check_control_6_4,
    "6.5": check_control_6_5,
    "6.6": check_control_6_6,
    "6.7": check_control_6_7,
}


class BenchmarkChecker:
    def __init__(self, profile_name=None, regions=None, verbose=False, project_name="security-audit", environment="lab"):
        self.profile_name = profile_name
        self.regions = regions
        self.verbose = verbose
        self.project_name = project_name
        self.environment = environment

        if verbose:
            logging.getLogger().setLevel(logging.DEBUG)

    def _prepare_report(self):
        account_id = get_account_id(profile_name=self.profile_name)
        if not account_id:
            logger.error("Could not retrieve AWS account ID. Please check your credentials.")
            return None

        if not self.regions:
            logger.info("Discovering AWS regions...")
            self.regions = get_all_regions(profile_name=self.profile_name)

        return BenchmarkReport(account_id, self.regions)

    def _run_controls(self, control_ids):
        report = self._prepare_report()
        if not report:
            return None

        for control_id in control_ids:
            check_func = CONTROLS.get(control_id)
            if not check_func:
                logger.warning(f"Control NET {control_id} not found")
                continue

            logger.info(f"Running check for NET {control_id}...")
            result = check_func(
                profile_name=self.profile_name,
                regions=self.regions,
                project_name=self.project_name,
                environment=self.environment,
            )

            if result:
                report.add_result(result)
                status_emoji = "✓" if result["status"] == "PASS" else "✗" if result["status"] == "FAIL" else "?"
                logger.info(f"  {status_emoji} NET {control_id}: {result['status']}")
            else:
                logger.warning(f"  No result returned for NET {control_id}")

        return report

    def run_all_checks(self):
        logger.info("Starting network benchmark checks...")
        return self._run_controls(sorted(CONTROLS.keys()))

    def run_specific_controls(self, control_ids):
        logger.info(f"Running specific controls: {', '.join(control_ids)}")
        return self._run_controls(control_ids)


def main():
    parser = argparse.ArgumentParser(
        description="Network benchmark checker (CIS 6.1-6.7)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python benchmark_checker.py
  python benchmark_checker.py -v
  python benchmark_checker.py --controls 6.1.1,6.3,6.5
  python benchmark_checker.py --controls 6.2,6.7
  python benchmark_checker.py --regions ap-southeast-1
  python benchmark_checker.py --output network-report.json
        """,
    )

    parser.add_argument("--controls", default=None, help="Specific controls to check (comma-separated, e.g. 6.1.1,6.3,6.5)")
    parser.add_argument("--regions", default=None, help="Specific regions to check (comma-separated)")
    parser.add_argument("--profile", default=None, help="AWS profile name")
    parser.add_argument("--output", default=None, help="Output file path for JSON report")
    parser.add_argument("--project-name", default="security-audit", help="Project tag value used to find resources")
    parser.add_argument("--environment", default="lab", help="Environment tag value used to find resources")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    regions = [region.strip() for region in args.regions.split(",")] if args.regions else None

    checker = BenchmarkChecker(
        profile_name=args.profile,
        regions=regions,
        verbose=args.verbose,
        project_name=args.project_name,
        environment=args.environment,
    )

    if args.controls:
        control_ids = [control.strip() for control in args.controls.split(",")]
        report = checker.run_specific_controls(control_ids)
    else:
        report = checker.run_all_checks()

    if not report:
        logger.error("Failed to generate report")
        sys.exit(1)

    print_report_summary(report)

    if args.output:
        logger.info(f"Saving report to {args.output}")
        if not report.save_to_file(args.output):
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
