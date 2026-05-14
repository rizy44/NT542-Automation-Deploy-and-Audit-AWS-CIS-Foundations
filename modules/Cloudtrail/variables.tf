variable "name_prefix" {
  description = "Prefix used for logging resource names."
  type        = string
}

variable "common_tags" {
  description = "Common tags applied to all logging resources."
  type        = map(string)
}

variable "cloudtrail_retention_days" {
  description = "Number of days to retain CloudTrail logs in S3."
  type        = number
  default     = 365

  validation {
    condition     = var.cloudtrail_retention_days >= 1
    error_message = "cloudtrail_retention_days must be at least 1."
  }
}

variable "config_snapshot_delivery_frequency" {
  description = "AWS Config snapshot delivery frequency."
  type        = string
  default     = "TwentyFour_Hours"

  validation {
    condition = contains([
      "One_Hour",
      "Three_Hours",
      "Six_Hours",
      "Twelve_Hours",
      "TwentyFour_Hours"
    ], var.config_snapshot_delivery_frequency)
    error_message = "config_snapshot_delivery_frequency must be a valid AWS Config delivery frequency."
  }
}

variable "enable_s3_data_event_read_logging" {
  description = "Whether CloudTrail records S3 object read data events."
  type        = bool
  default     = true
}

variable "enable_s3_data_event_write_logging" {
  description = "Whether CloudTrail records S3 object write data events."
  type        = bool
  default     = true
}
