"""
Utility module for benchmark output, summary, and safe error handling.
"""
import json
import logging
from datetime import datetime
from functools import wraps

from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger(__name__)


def get_iso_timestamp():
  return datetime.utcnow().isoformat() + "Z"


def error_handler(func):
  @wraps(func)
  def wrapper(*args, **kwargs):
    try:
      return func(*args, **kwargs)
    except ClientError as error:
      logger.error("Client error in %s: %s", func.__name__, error)
      return None
    except BotoCoreError as error:
      logger.error("BotoCore error in %s: %s", func.__name__, error)
      return None
    except Exception as error:
      logger.error("Unexpected error in %s: %s", func.__name__, error)
      return None

  return wrapper


def create_result(control_id, title, status, severity, details=None, resource_id=None, remediation=None):
  return {
    "control_id": f"CIS-{control_id}",
    "title": title,
    "status": status,
    "severity": severity,
    "resource_id": resource_id or "",
    "details": details or {},
    "remediation": remediation or "",
    "timestamp": get_iso_timestamp(),
  }


class BenchmarkReport:
  def __init__(self, aws_account_id, regions_checked):
    self.aws_account_id = aws_account_id
    self.regions_checked = regions_checked
    self.results = []
    self.start_time = get_iso_timestamp()

  def add_result(self, result):
    self.results.append(result)

  def get_summary(self):
    total = len(self.results)
    passed = sum(1 for result in self.results if result["status"] == "PASS")
    failed = sum(1 for result in self.results if result["status"] == "FAIL")
    unknown = sum(1 for result in self.results if result["status"] == "UNKNOWN")

    return {
      "total_controls": total,
      "passed": passed,
      "failed": failed,
      "unknown": unknown,
      "compliance_percentage": round((passed / total * 100) if total > 0 else 0, 2),
    }

  def to_dict(self):
    return {
      "benchmark_name": "CIS AWS Foundations Benchmark - Monitoring",
      "execution_date": self.start_time,
      "aws_account_id": self.aws_account_id,
      "regions_checked": self.regions_checked,
      "summary": self.get_summary(),
      "results": self.results,
    }

  def to_json(self, pretty=True):
    if pretty:
      return json.dumps(self.to_dict(), indent=2)
    return json.dumps(self.to_dict())

  def save_to_file(self, filepath):
    try:
      with open(filepath, "w", encoding="utf-8") as output:
        output.write(self.to_json(pretty=True))
      return True
    except IOError as error:
      logger.error("Failed to save report: %s", error)
      return False


def print_report_summary(report):
  summary = report.get_summary()
  print("\n" + "=" * 60)
  print("CIS AWS Monitoring Benchmark - Results Summary")
  print("=" * 60)
  print(f"Account ID: {report.aws_account_id}")
  print(f"Regions Checked: {', '.join(report.regions_checked)}")
  print(f"Execution Date: {report.start_time}")
  print("-" * 60)
  print(f"Total Controls: {summary['total_controls']}")
  print(f"Passed: {summary['passed']}")
  print(f"Failed: {summary['failed']}")
  print(f"Unknown: {summary['unknown']}")
  print(f"Compliance: {summary['compliance_percentage']}%")
  print("=" * 60)

  if summary["failed"] > 0:
    print("\nFailed Controls:")
    for result in report.results:
      if result["status"] == "FAIL":
        print(f"  - {result['control_id']}: {result['title']}")
        if result["remediation"]:
          print(f"    Remediation: {result['remediation']}")

  print()
