#!/usr/bin/env python3
"""
CIS AWS CloudTrail Benchmark Checker
Main entry point for running CIS compliance checks
"""
import sys
import argparse
import logging
from pathlib import Path

# Add checks folder to path
sys.path.insert(0, str(Path(__file__).parent))

from config import get_account_id, get_all_regions, CIS_CONTROLS
from utils import BenchmarkReport, print_report_summary, error_handler

# Import all control checks
from checks.control_3_1 import check_control_3_1
from checks.control_3_2 import check_control_3_2
from checks.control_3_3 import check_control_3_3
from checks.control_3_4 import check_control_3_4
from checks.control_3_5 import check_control_3_5
from checks.control_3_6 import check_control_3_6
from checks.control_3_7 import check_control_3_7
from checks.control_3_8 import check_control_3_8
from checks.control_3_9 import check_control_3_9

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Control mapping
CONTROLS = {
    "3.1": check_control_3_1,
    "3.2": check_control_3_2,
    "3.3": check_control_3_3,
    "3.4": check_control_3_4,
    "3.5": check_control_3_5,
    "3.6": check_control_3_6,
    "3.7": check_control_3_7,
    "3.8": check_control_3_8,
    "3.9": check_control_3_9,
}

class BenchmarkChecker:
    """
    Run CIS benchmark checks
    """
    def __init__(self, profile_name=None, regions=None, verbose=False):
        self.profile_name = profile_name
        self.regions = regions
        self.verbose = verbose
        
        if verbose:
            logging.getLogger().setLevel(logging.DEBUG)
    
    def run_all_checks(self):
        """Run all CIS controls"""
        logger.info("Starting CIS AWS CloudTrail Benchmark checks...")
        
        # Get account ID
        account_id = get_account_id(profile_name=self.profile_name)
        if not account_id:
            logger.error("Could not retrieve AWS account ID. Please check your credentials.")
            return None
        
        logger.info(f"Account ID: {account_id}")
        
        # Get regions
        if not self.regions:
            logger.info("Discovering AWS regions...")
            self.regions = get_all_regions(profile_name=self.profile_name)
        
        logger.info(f"Checking {len(self.regions)} regions: {', '.join(self.regions)}")
        
        # Create report
        report = BenchmarkReport(account_id, self.regions)
        
        # Run all controls
        for control_id in sorted(CONTROLS.keys()):
            logger.info(f"Running check for CIS {control_id}...")
            try:
                check_func = CONTROLS[control_id]
                result = check_func(
                    profile_name=self.profile_name,
                    regions=self.regions
                )
                
                if result:
                    report.add_result(result)
                    status_emoji = "✓" if result['status'] == 'PASS' else "✗" if result['status'] == 'FAIL' else "?"
                    logger.info(f"  {status_emoji} CIS {control_id}: {result['status']}")
                else:
                    logger.warning(f"  No result returned for CIS {control_id}")
            
            except Exception as e:
                logger.error(f"Error running check CIS {control_id}: {str(e)}")
        
        logger.info("All checks completed.")
        return report
    
    def run_specific_controls(self, control_ids):
        """Run specific controls"""
        logger.info(f"Running specific controls: {', '.join(control_ids)}")
        
        # Get account ID
        account_id = get_account_id(profile_name=self.profile_name)
        if not account_id:
            logger.error("Could not retrieve AWS account ID. Please check your credentials.")
            return None
        
        logger.info(f"Account ID: {account_id}")
        
        # Get regions
        if not self.regions:
            logger.info("Discovering AWS regions...")
            self.regions = get_all_regions(profile_name=self.profile_name)
        
        logger.info(f"Checking {len(self.regions)} regions")
        
        # Create report
        report = BenchmarkReport(account_id, self.regions)
        
        # Run specific controls
        for control_id in control_ids:
            if control_id not in CONTROLS:
                logger.warning(f"Control CIS {control_id} not found")
                continue
            
            logger.info(f"Running check for CIS {control_id}...")
            try:
                check_func = CONTROLS[control_id]
                result = check_func(
                    profile_name=self.profile_name,
                    regions=self.regions
                )
                
                if result:
                    report.add_result(result)
                    status_emoji = "✓" if result['status'] == 'PASS' else "✗" if result['status'] == 'FAIL' else "?"
                    logger.info(f"  {status_emoji} CIS {control_id}: {result['status']}")
                else:
                    logger.warning(f"  No result returned for CIS {control_id}")
            
            except Exception as e:
                logger.error(f"Error running check CIS {control_id}: {str(e)}")
        
        logger.info("Selected checks completed.")
        return report

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='CIS AWS CloudTrail Benchmark Checker',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all checks
  python benchmark_checker.py
  
  # Run all checks with verbose output
  python benchmark_checker.py -v
  
  # Run specific controls
  python benchmark_checker.py --controls 3.1,3.2,3.3
  
  # Run all checks and save to file
  python benchmark_checker.py --output report.json
  
  # Run with specific AWS profile and regions
  python benchmark_checker.py --profile prod --regions us-east-1,eu-west-1
        """
    )
    
    parser.add_argument(
        '--controls',
        help='Specific controls to check (comma-separated, e.g., 3.1,3.2)',
        default=None
    )
    
    parser.add_argument(
        '--regions',
        help='Specific regions to check (comma-separated)',
        default=None
    )
    
    parser.add_argument(
        '--profile',
        help='AWS profile name',
        default=None
    )
    
    parser.add_argument(
        '--output',
        help='Output file path for JSON report',
        default=None
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )
    
    args = parser.parse_args()
    
    # Parse regions if provided
    regions = None
    if args.regions:
        regions = [r.strip() for r in args.regions.split(',')]
    
    # Create checker
    checker = BenchmarkChecker(
        profile_name=args.profile,
        regions=regions,
        verbose=args.verbose
    )
    
    # Run checks
    if args.controls:
        control_ids = [c.strip() for c in args.controls.split(',')]
        report = checker.run_specific_controls(control_ids)
    else:
        report = checker.run_all_checks()
    
    if not report:
        logger.error("Failed to generate report")
        sys.exit(1)
    
    # Print summary
    print_report_summary(report)
    
    # Save to file if requested
    if args.output:
        logger.info(f"Saving report to {args.output}")
        if report.save_to_file(args.output):
            logger.info(f"Report successfully saved to {args.output}")
        else:
            logger.error("Failed to save report")
            sys.exit(1)
    
    # Print JSON to stdout
    print("\n" + "="*60)
    print("Full JSON Report:")
    print("="*60)
    print(report.to_json(pretty=True))
    
    # Exit with appropriate code
    summary = report.get_summary()
    if summary['failed'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == '__main__':
    main()
