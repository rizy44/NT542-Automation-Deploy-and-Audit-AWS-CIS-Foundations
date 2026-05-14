#!/usr/bin/env python3
"""
CIS AWS Monitoring Benchmark Checker
Checks section 5.1 through 5.16.
"""
import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from checks.monitoring_controls import (  # noqa: E402
  check_control_5_16,
  check_metric_filter_alarm_control,
)
from config import CIS_CONTROLS, get_account_id, get_all_regions  # noqa: E402
from utils import BenchmarkReport, print_report_summary  # noqa: E402

logging.basicConfig(
  level=logging.INFO,
  format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

METRIC_FILTER_CONTROLS = [
  "5.1",
  "5.2",
  "5.3",
  "5.4",
  "5.5",
]


class BenchmarkChecker:
  def __init__(self, profile_name=None, regions=None, log_group_name=None, metric_namespace="CISBenchmark", verbose=False):
    self.profile_name = profile_name
    self.regions = regions
    self.log_group_name = log_group_name
    self.metric_namespace = metric_namespace

    if verbose:
      logging.getLogger().setLevel(logging.DEBUG)

  def _init_report(self):
    account_id = get_account_id(profile_name=self.profile_name)
    if not account_id:
      logger.error("Could not retrieve AWS account ID. Check credentials and permissions.")
      return None

    if not self.regions:
      self.regions = get_all_regions(profile_name=self.profile_name)

    if not self.regions:
      logger.error("No regions available for scanning.")
      return None

    return BenchmarkReport(account_id, self.regions)

  def _run_control(self, control_id):
    if control_id == "5.16":
      return check_control_5_16(profile_name=self.profile_name, regions=self.regions)

    return check_metric_filter_alarm_control(
      control_id=control_id,
      profile_name=self.profile_name,
      regions=self.regions,
      log_group_name=self.log_group_name,
      metric_namespace=self.metric_namespace,
    )

  def run_controls(self, control_ids):
    report = self._init_report()
    if not report:
      return None

    for control_id in control_ids:
      if control_id not in CIS_CONTROLS:
        logger.warning("Control CIS %s not found", control_id)
        continue

      logger.info("Running check for CIS %s", control_id)
      result = self._run_control(control_id)
      if result:
        report.add_result(result)

    return report


def parse_controls(control_arg):
  if not control_arg:
    return METRIC_FILTER_CONTROLS
  return [item.strip() for item in control_arg.split(",") if item.strip()]


def main():
  parser = argparse.ArgumentParser(
    description="CIS AWS Monitoring Benchmark Checker",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="""
Examples:
  python benchmark_checker.py --log-group /aws/cloudtrail/main-cloudtrail
  python benchmark_checker.py --controls 5.1,5.2,5.16 --log-group /aws/cloudtrail/main-cloudtrail
  python benchmark_checker.py --profile prod --regions us-east-1,ap-southeast-1 --output monitor-report.json --log-group /aws/cloudtrail/org-trail
    """,
  )

  parser.add_argument("--controls", default=None, help="Comma-separated controls, e.g. 5.1,5.2,5.16")
  parser.add_argument("--regions", default=None, help="Comma-separated regions")
  parser.add_argument("--profile", default=None, help="AWS profile name")
  parser.add_argument("--output", default=None, help="Output JSON report file")
  parser.add_argument("--log-group", required=True, help="CloudWatch log group receiving CloudTrail events")
  parser.add_argument("--namespace", default="CISBenchmark", help="Metric namespace (default: CISBenchmark)")
  parser.add_argument("-v", "--verbose", action="store_true", help="Verbose logging")

  args = parser.parse_args()

  regions = None
  if args.regions:
    regions = [item.strip() for item in args.regions.split(",") if item.strip()]

  controls = parse_controls(args.controls)

  checker = BenchmarkChecker(
    profile_name=args.profile,
    regions=regions,
    log_group_name=args.log_group,
    metric_namespace=args.namespace,
    verbose=args.verbose,
  )

  report = checker.run_controls(controls)
  if not report:
    sys.exit(1)

  print_report_summary(report)

  if args.output and not report.save_to_file(args.output):
    sys.exit(1)

  print("\n" + "=" * 60)
  print("Full JSON Report:")
  print("=" * 60)
  print(report.to_json(pretty=True))

  summary = report.get_summary()
  if summary["failed"] > 0:
    sys.exit(1)
  sys.exit(0)


if __name__ == "__main__":
  main()
