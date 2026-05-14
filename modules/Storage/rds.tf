resource "aws_db_subnet_group" "main" {
  name        = "storage-db-subnet-group-${var.environment}"
  description = "DB subnet group for RDS MySQL across two private subnets"
  subnet_ids  = var.private_subnet_ids

  tags = merge(local.common_tags, {
    Name = "storage-db-subnet-group-${var.environment}"
  })
}


resource "aws_security_group" "rds" {
  name        = "storage-rds-sg-${var.environment}"
  description = "Allow MySQL/Aurora traffic from within the imported VPC only"
  vpc_id      = var.vpc_id

  ingress {
    description = "MySQL from VPC CIDR"
    from_port   = 3306
    to_port     = 3306
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
    Name = "storage-rds-sg-${var.environment}"
  })
}


resource "aws_db_parameter_group" "mysql8" {
  name        = "storage-mysql8-params-${var.environment}"
  family      = "mysql8.0"
  description = "MySQL 8.0 parameter group with CIS-aligned settings"

  # Enforce SSL/TLS connections (CIS)
  parameter {
    name         = "require_secure_transport"
    value        = "ON"
    apply_method = "immediate"
  }

  tags = merge(local.common_tags, {
    Name = "storage-mysql8-params-${var.environment}"
  })
}


resource "aws_db_option_group" "mysql8_audit" {
  name                     = "storage-mysql8-audit-${var.environment}"
  engine_name              = "mysql"
  major_engine_version     = "8.0"
  option_group_description = "MySQL 8.0 option group enabling connection and query audit logging"

  option {
    option_name = "MARIADB_AUDIT_PLUGIN"

    option_settings {
      name  = "SERVER_AUDIT_EVENTS"
      value = "CONNECT,QUERY_DDL,QUERY_DML,QUERY_DCL"
    }

    option_settings {
      name  = "SERVER_AUDIT_EXCL_USERS"
      value = "rdsadmin"
    }
  }

  tags = merge(local.common_tags, {
    Name = "storage-mysql8-audit-${var.environment}"
  })
}


resource "aws_iam_role" "rds_monitoring" {
  name        = "storage-rds-monitoring-${var.environment}"
  description = "Allows RDS to push enhanced monitoring metrics to CloudWatch"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid    = "AllowRDSMonitoringAssume"
      Effect = "Allow"
      Principal = {
        Service = "monitoring.rds.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })

  tags = merge(local.common_tags, {
    Name = "storage-rds-monitoring-${var.environment}"
  })
}

resource "aws_iam_role_policy_attachment" "rds_monitoring" {
  role       = aws_iam_role.rds_monitoring.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

# ---------------------------------------------------------------------------
# RDS – MySQL 8.0 Instance
#   CIS 2.3.1  –  storage_encrypted = true  (KMS)
#   CIS 2.3.2  –  auto_minor_version_upgrade = true
#   CIS 2.3.3  –  backup_retention_period > 0
#   CIS        –  publicly_accessible = false, placed in private subnets
# ---------------------------------------------------------------------------

resource "aws_db_instance" "mysql" {
  identifier        = "storage-mysql-${var.environment}"
  engine            = "mysql"
  engine_version    = var.rds_engine_version
  instance_class    = var.rds_instance_class
  allocated_storage = var.rds_allocated_storage
  storage_type      = "gp3"

  db_name  = var.rds_db_name
  username = var.rds_master_username
  password = var.rds_master_password

  storage_encrypted = true
  kms_key_id        = aws_kms_key.rds.arn

  backup_retention_period  = var.rds_backup_retention_days
  backup_window            = "03:00-04:00"
  maintenance_window       = "sun:04:00-sun:05:00"
  delete_automated_backups = true

  publicly_accessible = false

  auto_minor_version_upgrade = true

  multi_az = var.rds_multi_az

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  parameter_group_name   = aws_db_parameter_group.mysql8.name
  option_group_name      = aws_db_option_group.mysql8_audit.name

  monitoring_interval = 60
  monitoring_role_arn = aws_iam_role.rds_monitoring.arn

  performance_insights_enabled          = true
  performance_insights_kms_key_id       = aws_kms_key.rds.arn
  performance_insights_retention_period = 7

  enabled_cloudwatch_logs_exports = ["audit", "error", "general", "slowquery"]

  deletion_protection = false

  skip_final_snapshot = true

  tags = merge(local.common_tags, {
    Name = "storage-mysql-${var.environment}"
  })

  depends_on = [
    aws_db_subnet_group.main,
    aws_db_parameter_group.mysql8,
    aws_db_option_group.mysql8_audit,
    aws_iam_role_policy_attachment.rds_monitoring,
    aws_kms_key.rds
  ]
}
