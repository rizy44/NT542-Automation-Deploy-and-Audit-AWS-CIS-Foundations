"""
Utility Module
Handles JSON output formatting, error handling, and helper functions
"""
import json
import logging
from datetime import datetime
from functools import wraps
from botocore.exceptions import ClientError, BotoCoreError

logger = logging.getLogger(__name__)

def get_iso_timestamp():
    """Get current timestamp in ISO format"""
    return datetime.utcnow().isoformat() + "Z"

def error_handler(func):
    """
    Decorator to handle errors in check functions
    Returns UNKNOWN status on permission/API errors
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            if error_code in ['AccessDenied', 'UnauthorizedOperation', 'NoCredentialProviders']:
                logger.warning(f"Permission denied in {func.__name__}: {str(e)}")
                return None  # Will be handled as UNKNOWN
            else:
                logger.error(f"Client error in {func.__name__}: {str(e)}")
                return None
        except BotoCoreError as e:
            logger.error(f"BotoCore error in {func.__name__}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
            return None
    return wrapper

def create_result(control_id, title, status, severity, details=None, resource_id=None, remediation=None):
    """
    Create a CIS control result
    
    Args:
        control_id: CIS control ID (e.g., "3.1")
        title: Control title
        status: PASS / FAIL / UNKNOWN
        severity: CRITICAL / HIGH / MEDIUM / LOW
        details: Additional details (dict)
        resource_id: Resource identifier
        remediation: Remediation recommendation
    
    Returns:
        dict with result structure
    """
    return {
        "control_id": f"CIS-{control_id}",
        "title": title,
        "status": status,
        "severity": severity,
        "resource_id": resource_id or "",
        "details": details or {},
        "remediation": remediation or "",
        "timestamp": get_iso_timestamp()
    }

class BenchmarkReport:
    """
    Build and manage benchmark report
    """
    def __init__(self, aws_account_id, regions_checked):
        self.aws_account_id = aws_account_id
        self.regions_checked = regions_checked
        self.results = []
        self.start_time = get_iso_timestamp()
    
    def add_result(self, result):
        """Add a control result to the report"""
        self.results.append(result)
    
    def add_results(self, results):
        """Add multiple control results"""
        self.results.extend([r for r in results if r])
    
    def get_summary(self):
        """Get summary statistics"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r['status'] == 'PASS')
        failed = sum(1 for r in self.results if r['status'] == 'FAIL')
        unknown = sum(1 for r in self.results if r['status'] == 'UNKNOWN')
        
        return {
            "total_controls": total,
            "passed": passed,
            "failed": failed,
            "unknown": unknown,
            "compliance_percentage": round((passed / total * 100) if total > 0 else 0, 2)
        }
    
    def to_dict(self):
        """Convert report to dictionary"""
        return {
            "benchmark_name": "CIS AWS Foundations Benchmark - CloudTrail",
            "execution_date": self.start_time,
            "aws_account_id": self.aws_account_id,
            "regions_checked": self.regions_checked,
            "summary": self.get_summary(),
            "results": self.results
        }
    
    def to_json(self, pretty=True):
        """Convert report to JSON string"""
        if pretty:
            return json.dumps(self.to_dict(), indent=2)
        else:
            return json.dumps(self.to_dict())
    
    def save_to_file(self, filepath):
        """Save report to JSON file"""
        try:
            with open(filepath, 'w') as f:
                f.write(self.to_json(pretty=True))
            logger.info(f"Report saved to {filepath}")
            return True
        except IOError as e:
            logger.error(f"Failed to save report: {str(e)}")
            return False

def print_report_summary(report):
    """Pretty print report summary to console"""
    summary = report.get_summary()
    print("\n" + "="*60)
    print("CIS AWS CloudTrail Benchmark - Results Summary")
    print("="*60)
    print(f"Account ID: {report.aws_account_id}")
    print(f"Regions Checked: {', '.join(report.regions_checked)}")
    print(f"Execution Date: {report.start_time}")
    print("-"*60)
    print(f"Total Controls: {summary['total_controls']}")
    print(f"✓ Passed: {summary['passed']}")
    print(f"✗ Failed: {summary['failed']}")
    print(f"? Unknown: {summary['unknown']}")
    print(f"Compliance: {summary['compliance_percentage']}%")
    print("="*60)
    
    # Print failed controls
    if summary['failed'] > 0:
        print("\n⚠ Failed Controls:")
        for result in report.results:
            if result['status'] == 'FAIL':
                print(f"  - {result['control_id']}: {result['title']}")
                if result['remediation']:
                    print(f"    Remediation: {result['remediation']}")
    
    print()
