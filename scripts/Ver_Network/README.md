# Network Benchmark Checker

This folder contains a comprehensive network audit script that follows the **CIS AWS Foundations Benchmark** Section 6 (Networking) controls from **CIS 6.1 to 6.7**.

## Structure

1. Central runner: `benchmark_checker.py`
2. Shared AWS helpers: `config.py`
3. Shared reporting & error handling: `utils.py`
4. One control per file in `checks/`

## CIS Controls Implemented

This benchmark implements all 8 CIS networking controls:

- **6.1.1** - Ensure EBS volume encryption is enabled in all regions (Automated)
- **6.1.2** - Ensure CIFS access is restricted to trusted networks (Automated)
- **6.2** - Ensure no Network ACLs allow ingress from 0.0.0.0/0 to SSH/RDP (Automated)
- **6.3** - Ensure no security groups allow ingress from 0.0.0.0/0 to SSH/RDP (Automated)
- **6.4** - Ensure no security groups allow ingress from ::/0 to SSH/RDP (Automated)
- **6.5** - Ensure the default security group of every VPC restricts all traffic (Automated)
- **6.6** - Ensure routing tables for VPC peering are least access (Manual)
- **6.7** - Ensure that the EC2 Metadata Service only allows IMDSv2 (Automated)

## Requirements

Install AWS Python packages:

```bash
pip install -r requirements.txt
```

## Usage

Run all CIS 6.x controls:

```bash
python scripts/Ver_Network/benchmark_checker.py
```

Run a specific control:

```bash
python scripts/Ver_Network/benchmark_checker.py --controls 6.1.1,6.3,6.5
```

Use a specific profile and region:

```bash
python scripts/Ver_Network/benchmark_checker.py --profile prod --regions ap-southeast-1
```

Save a JSON report:

```bash
python scripts/Ver_Network/benchmark_checker.py --output network-cis-report.json
```

Verbose output:

```bash
python scripts/Ver_Network/benchmark_checker.py -v
```

## Reading Order

For learning how each CIS control is implemented, read in this order:

1. `benchmark_checker.py` — Main entry point and control dispatcher
2. `config.py` — AWS client setup and CIS control definitions
3. `utils.py` — Report generation and error handling
4. `checks/control_6_1_1.py` — EBS encryption check
5. `checks/control_6_1_2.py` — CIFS access restriction check
6. `checks/control_6_2.py` — NACL SSH/RDP check
7. `checks/control_6_3.py` — Security Group SSH/RDP IPv4 check
8. `checks/control_6_4.py` — Security Group SSH/RDP IPv6 check
9. `checks/control_6_5.py` — Default SG restrictive check
10. `checks/control_6_6.py` — VPC peering routing least access (Manual)
11. `checks/control_6_7.py` — IMDSv2 required check

## Report Output

The tool generates a summary report and full JSON report with:
- Total controls checked
- Pass/Fail/Unknown counts
- Compliance percentage
- Detailed findings for each control
- Remediation recommendations for failed controls
