resource "aws_efs_file_system" "main" {
  creation_token   = "storage-efs-${var.environment}"
  encrypted        = true
  kms_key_id       = aws_kms_key.efs.arn
  performance_mode = var.efs_performance_mode
  throughput_mode  = var.efs_throughput_mode

  # Automatic lifecycle management
  lifecycle_policy {
    transition_to_ia = "AFTER_30_DAYS"
  }

  lifecycle_policy {
    transition_to_primary_storage_class = "AFTER_1_ACCESS"
  }

  tags = merge(local.common_tags, {
    Name = "storage-efs-${var.environment}"
  })
}


resource "aws_efs_backup_policy" "main" {
  file_system_id = aws_efs_file_system.main.id

  backup_policy {
    status = "ENABLED"
  }
}


resource "aws_security_group" "efs" {
  name        = "storage-efs-sg-${var.environment}"
  description = "Allow NFS traffic from within the imported VPC only"
  vpc_id      = var.vpc_id

  ingress {
    description = "NFS from VPC CIDR"
    from_port   = 2049
    to_port     = 2049
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr_block]
  }

  egress {
    description = "Allow all outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "storage-efs-sg-${var.environment}"
  })
}


resource "aws_efs_mount_target" "az_a" {
  file_system_id  = aws_efs_file_system.main.id
  subnet_id       = var.private_subnet_ids[0]
  security_groups = [aws_security_group.efs.id]
}

resource "aws_efs_mount_target" "az_b" {
  file_system_id  = aws_efs_file_system.main.id
  subnet_id       = var.private_subnet_ids[1]
  security_groups = [aws_security_group.efs.id]
}


resource "aws_efs_access_point" "app" {
  file_system_id = aws_efs_file_system.main.id

  posix_user {
    gid = 1000
    uid = 1000
  }

  root_directory {
    path = "/app-data"
    creation_info {
      owner_gid   = 1000
      owner_uid   = 1000
      permissions = "755"
    }
  }

  tags = merge(local.common_tags, {
    Name = "storage-efs-ap-${var.environment}"
  })
}


resource "aws_efs_file_system_policy" "main" {
  file_system_id = aws_efs_file_system.main.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "EnforceEncryptedTransport"
        Effect = "Deny"
        Principal = {
          AWS = "*"
        }
        Action   = "*"
        Resource = aws_efs_file_system.main.arn
        Condition = {
          Bool = {
            "aws:SecureTransport" = "false"
          }
        }
      }
    ]
  })
}
