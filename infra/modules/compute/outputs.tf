output "app_security_group_id" {
  description = "Security group ID for app instances."
  value       = aws_security_group.app.id
}

output "app_instance_ids" {
  description = "IDs of app instances."
  value       = aws_instance.app[*].id
}

output "app_instance_private_ips" {
  description = "Private IP addresses of app instances."
  value       = aws_instance.app[*].private_ip
}

output "app_instance_subnet_ids" {
  description = "Subnet IDs used by app instances."
  value       = aws_instance.app[*].subnet_id
}

output "app_instance_profile_name" {
  description = "IAM instance profile name attached to app instances."
  value       = aws_iam_instance_profile.app.name
}

output "app_instance_role_name" {
  description = "IAM role name used by app instances."
  value       = aws_iam_role.app_instance.name
}
