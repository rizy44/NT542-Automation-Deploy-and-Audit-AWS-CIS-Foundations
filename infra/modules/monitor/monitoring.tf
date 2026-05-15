locals {
  cis_monitoring_filters = {
    unauthorized_api_calls = {
      metric_name    = "UnauthorizedAPICalls"
      alarm_name     = "cis-5-1-unauthorized-api-calls-${var.environment}"
      alarm_desc     = "CIS 5.1 - Unauthorized API calls detected"
      filter_pattern = "{ ($.errorCode = \"*UnauthorizedOperation\") || ($.errorCode = \"AccessDenied*\") && ($.sourceIPAddress!=\"delivery.logs.amazonaws.com\") && ($.eventName!=\"HeadBucket\") }"
    }

    console_signin_without_mfa = {
      metric_name    = "ConsoleSigninWithoutMFA"
      alarm_name     = "cis-5-2-console-signin-no-mfa-${var.environment}"
      alarm_desc     = "CIS 5.2 - Console sign-in without MFA detected"
      filter_pattern = "{ ($.eventName = \"ConsoleLogin\") && ($.additionalEventData.MFAUsed != \"Yes\") }"
    }

    root_usage = {
      metric_name    = "RootAccountUsage"
      alarm_name     = "cis-5-3-root-account-usage-${var.environment}"
      alarm_desc     = "CIS 5.3 - Root account usage detected"
      filter_pattern = "{ ($.userIdentity.type = \"Root\") && ($.userIdentity.invokedBy NOT EXISTS) && ($.eventType != \"AwsServiceEvent\") }"
    }

    iam_policy_changes = {
      metric_name    = "IAMPolicyChanges"
      alarm_name     = "cis-5-4-iam-policy-changes-${var.environment}"
      alarm_desc     = "CIS 5.4 - IAM policy changes detected"
      filter_pattern = "{ (($.eventName = \"DeleteGroupPolicy\") || ($.eventName = \"DeleteRolePolicy\") || ($.eventName = \"DeleteUserPolicy\") || ($.eventName = \"PutGroupPolicy\") || ($.eventName = \"PutRolePolicy\") || ($.eventName = \"PutUserPolicy\") || ($.eventName = \"CreatePolicy\") || ($.eventName = \"DeletePolicy\") || ($.eventName = \"CreatePolicyVersion\") || ($.eventName = \"DeletePolicyVersion\") || ($.eventName = \"AttachRolePolicy\") || ($.eventName = \"DetachRolePolicy\") || ($.eventName = \"AttachUserPolicy\") || ($.eventName = \"DetachUserPolicy\") || ($.eventName = \"AttachGroupPolicy\") || ($.eventName = \"DetachGroupPolicy\")) }"
    }

    cloudtrail_changes = {
      metric_name    = "CloudTrailConfigChanges"
      alarm_name     = "cis-5-5-cloudtrail-config-changes-${var.environment}"
      alarm_desc     = "CIS 5.5 - CloudTrail configuration changes detected"
      filter_pattern = "{ (($.eventName = \"CreateTrail\") || ($.eventName = \"UpdateTrail\") || ($.eventName = \"DeleteTrail\") || ($.eventName = \"StartLogging\") || ($.eventName = \"StopLogging\")) }"
    }
  }
}

locals {
  monitored_filters = length(var.enabled_controls) > 0 ? { for k, v in local.cis_monitoring_filters : k => v if contains(var.enabled_controls, k) } : local.cis_monitoring_filters
}

locals {
  sns_topic_arn = var.sns_topic_arn != "" ? var.sns_topic_arn : (length(aws_sns_topic.cis_monitoring) > 0 ? aws_sns_topic.cis_monitoring[0].arn : "")
}

resource "aws_sns_topic" "cis_monitoring" {
  count = var.sns_topic_arn == "" ? 1 : 0
  name  = var.sns_topic_name

  tags = merge(local.common_tags, {
    Name = var.sns_topic_name
  })
}

resource "aws_sns_topic_subscription" "email" {
  for_each  = toset(var.alarm_notification_emails)
  topic_arn = local.sns_topic_arn
  protocol  = "email"
  endpoint  = each.value
}

resource "aws_cloudwatch_log_group" "cloudtrail" {
  name = var.cloudtrail_log_group_name

  tags = merge(local.common_tags, {
    Name = var.cloudtrail_log_group_name
  })
}


resource "aws_cloudwatch_log_metric_filter" "cis" {
  for_each = var.create_metric_filters ? local.monitored_filters : {}

  name           = "cis-${each.key}-${var.environment}"
  pattern        = each.value.filter_pattern
  log_group_name = var.cloudtrail_log_group_name

  depends_on = [aws_cloudwatch_log_group.cloudtrail]

  metric_transformation {
    name      = each.value.metric_name
    namespace = var.metric_namespace
    value     = "1"
  }
}


resource "aws_cloudwatch_metric_alarm" "cis" {
  for_each = var.create_metric_filters ? local.monitored_filters : {}

  alarm_name          = each.value.alarm_name
  alarm_description   = each.value.alarm_desc
  namespace           = var.metric_namespace
  metric_name         = each.value.metric_name
  statistic           = "Sum"
  period              = 300
  evaluation_periods  = 1
  threshold           = 1
  comparison_operator = "GreaterThanOrEqualToThreshold"
  treat_missing_data  = "notBreaching"

  alarm_actions = [local.sns_topic_arn]
  ok_actions    = [local.sns_topic_arn]

  tags = merge(local.common_tags, {
    Name = each.value.alarm_name
  })

  depends_on = [aws_cloudwatch_log_metric_filter.cis]
}

resource "aws_securityhub_account" "this" {
  count = var.enable_security_hub ? 1 : 0
}
