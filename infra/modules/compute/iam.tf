data "aws_iam_policy_document" "app_instance_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "app_instance" {
  count = var.enable_iam_profile ? 1 : 0

  name               = "${var.name_prefix}-role-app-instance"
  assume_role_policy = data.aws_iam_policy_document.app_instance_assume_role.json

  tags = merge(local.module_tags, {
    Name = "${var.name_prefix}-role-app-instance"
  })
}

resource "aws_iam_role_policy_attachment" "ssm_core" {
  count = var.enable_iam_profile ? 1 : 0

  role       = aws_iam_role.app_instance[0].name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_instance_profile" "app" {
  count = var.enable_iam_profile ? 1 : 0

  name = "${var.name_prefix}-profile-app"
  role = aws_iam_role.app_instance[0].name

  tags = merge(local.module_tags, {
    Name = "${var.name_prefix}-profile-app"
  })
}
