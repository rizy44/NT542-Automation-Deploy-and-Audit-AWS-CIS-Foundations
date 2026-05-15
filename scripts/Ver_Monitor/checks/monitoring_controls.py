"""
Control checks for CIS monitoring section 5.x.
"""
import logging

from botocore.exceptions import ClientError

from config import CIS_CONTROLS, get_client
from utils import create_result, error_handler

logger = logging.getLogger(__name__)


def _get_metric_filter(regions, profile_name, log_group_name, metric_namespace, metric_name):
  findings = []

  for region in regions:
    logs_client = get_client("logs", region_name=region, profile_name=profile_name)
    try:
      paginator = logs_client.get_paginator("describe_metric_filters")
      for page in paginator.paginate(logGroupName=log_group_name):
        for metric_filter in page.get("metricFilters", []):
          transformations = metric_filter.get("metricTransformations", [])
          for transformation in transformations:
            if (
              transformation.get("metricName") == metric_name
              and transformation.get("metricNamespace") == metric_namespace
            ):
              findings.append(
                {
                  "region": region,
                  "filter_name": metric_filter.get("filterName"),
                  "pattern": metric_filter.get("filterPattern"),
                }
              )
    except ClientError as error:
      code = error.response.get("Error", {}).get("Code", "")
      if code == "ResourceNotFoundException":
        logger.debug("Log group %s not found in %s", log_group_name, region)
        continue
      raise

  return findings


def _get_valid_alarm(regions, profile_name, metric_namespace, metric_name):
  findings = []

  for region in regions:
    cloudwatch_client = get_client("cloudwatch", region_name=region, profile_name=profile_name)
    next_token = None
    while True:
      request = {
        "Namespace": metric_namespace,
        "MetricName": metric_name,
      }
      if next_token:
        request["NextToken"] = next_token

      response = cloudwatch_client.describe_alarms_for_metric(**request)
      for alarm in response.get("MetricAlarms", []):
        is_valid = (
          alarm.get("ComparisonOperator") == "GreaterThanOrEqualToThreshold"
          and alarm.get("Period") == 300
          and alarm.get("EvaluationPeriods") == 1
          and float(alarm.get("Threshold", 0)) >= 1
          and len(alarm.get("AlarmActions", [])) > 0
        )
        if is_valid:
          findings.append(
            {
              "region": region,
              "alarm_name": alarm.get("AlarmName"),
              "threshold": alarm.get("Threshold"),
              "period": alarm.get("Period"),
              "evaluation_periods": alarm.get("EvaluationPeriods"),
            }
          )

      next_token = response.get("NextToken")
      if not next_token:
        break

  return findings


@error_handler
def check_metric_filter_alarm_control(control_id, profile_name=None, regions=None, log_group_name=None, metric_namespace="CISBenchmark"):
  control = CIS_CONTROLS[control_id]
  metric_name = control["metric_name"]

  filter_findings = _get_metric_filter(
    regions=regions,
    profile_name=profile_name,
    log_group_name=log_group_name,
    metric_namespace=metric_namespace,
    metric_name=metric_name,
  )

  alarm_findings = _get_valid_alarm(
    regions=regions,
    profile_name=profile_name,
    metric_namespace=metric_namespace,
    metric_name=metric_name,
  )

  if filter_findings and alarm_findings:
    return create_result(
      control_id,
      control["title"],
      "PASS",
      control["severity"],
      details={
        "log_group_name": log_group_name,
        "metric_namespace": metric_namespace,
        "metric_name": metric_name,
        "metric_filters": filter_findings,
        "alarms": alarm_findings,
      },
      resource_id=metric_name,
    )

  return create_result(
    control_id,
    control["title"],
    "FAIL",
    control["severity"],
    details={
      "log_group_name": log_group_name,
      "metric_namespace": metric_namespace,
      "metric_name": metric_name,
      "metric_filters_found": len(filter_findings),
      "alarms_found": len(alarm_findings),
      "metric_filters": filter_findings,
      "alarms": alarm_findings,
    },
    resource_id=metric_name,
    remediation="Create matching CloudWatch metric filter and alarm for this control",
  )


@error_handler
def check_control_5_16(profile_name=None, regions=None, **_):
  control_id = "5.16"
  control = CIS_CONTROLS[control_id]

  enabled_regions = []
  disabled_regions = []

  for region in regions:
    client = get_client("securityhub", region_name=region, profile_name=profile_name)
    try:
      client.describe_hub()
      enabled_regions.append(region)
    except ClientError as error:
      code = error.response.get("Error", {}).get("Code", "")
      if code in ["InvalidAccessException", "ResourceNotFoundException"]:
        disabled_regions.append(region)
      else:
        raise

  if not disabled_regions and enabled_regions:
    return create_result(
      control_id,
      control["title"],
      "PASS",
      control["severity"],
      details={"enabled_regions": enabled_regions},
      resource_id="securityhub",
    )

  return create_result(
    control_id,
    control["title"],
    "FAIL",
    control["severity"],
    details={
      "enabled_regions": enabled_regions,
      "disabled_regions": disabled_regions,
    },
    resource_id="securityhub",
    remediation="Enable Security Hub in all target regions",
  )
