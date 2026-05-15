"""
Utility helpers for the network benchmark.
"""
import json
import logging
from datetime import datetime
from functools import wraps

try:
    from botocore.exceptions import BotoCoreError, ClientError
except ImportError:  # pragma: no cover - handled at runtime with a clear error
    BotoCoreError = Exception
    ClientError = Exception

logger = logging.getLogger(__name__)


def get_iso_timestamp():
    return datetime.utcnow().isoformat() + "Z"


def error_handler(func):
    """Convert AWS errors into a safe UNKNOWN result path."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ClientError as error:
            error_code = error.response.get("Error", {}).get("Code", "Unknown")
            if error_code in {"AccessDenied", "UnauthorizedOperation", "NoCredentialProviders"}:
                logger.warning(f"Permission denied in {func.__name__}: {error}")
            else:
                logger.error(f"Client error in {func.__name__}: {error}")
            return None
        except BotoCoreError as error:
            logger.error(f"BotoCore error in {func.__name__}: {error}")
            return None
        except Exception as error:
            logger.error(f"Unexpected error in {func.__name__}: {error}")
            return None

    return wrapper


def create_result(control_id, title, status, severity, details=None, resource_id=None, remediation=None):
    return {
        "control_id": f"NET-{control_id}",
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
            "benchmark_name": "Network Benchmark - Project Infrastructure",
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
            with open(filepath, "w", encoding="utf-8") as file_handle:
                file_handle.write(self.to_json(pretty=True))
            return True
        except OSError as error:
            logger.error(f"Failed to save report: {error}")
            return False


def print_report_summary(report):
    summary = report.get_summary()
    print("\n" + "=" * 60)
    print("Network Benchmark - Results Summary")
    print("=" * 60)
    print(f"Account ID: {report.aws_account_id}")
    print(f"Regions Checked: {', '.join(report.regions_checked)}")
    print(f"Execution Date: {report.start_time}")
    print("-" * 60)
    print(f"Total Controls: {summary['total_controls']}")
    print(f"✓ Passed: {summary['passed']}")
    print(f"✗ Failed: {summary['failed']}")
    print(f"? Unknown: {summary['unknown']}")
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
