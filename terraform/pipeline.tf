resource "aws_iam_role" "code_build_iam" {
  name = "CodeBuildIAM"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "codebuild.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "code_build_iam_policy" {
  role = aws_iam_role.code_build_iam.name

  policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Resource": [
        "*"
      ],
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "ec2:CreateNetworkInterface",
        "ec2:DescribeDhcpOptions",
        "ec2:DescribeNetworkInterfaces",
        "ec2:DeleteNetworkInterface",
        "ec2:DescribeSubnets",
        "ec2:DescribeSecurityGroups",
        "ec2:DescribeVpcs"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ec2:CreateNetworkInterfacePermission"
      ],
      "Resource": [
"arn:aws:ec2:${data.aws_region.region.name}:${data.aws_caller_identity.current.account_id}:network-interface/*"
      ]
    }
  ]
}
POLICY
}

resource "aws_codebuild_source_credential" "github_access_token" {
  auth_type   = "PERSONAL_ACCESS_TOKEN"
  server_type = "GITHUB_ENTERPRISE"
  token       = var.github_personal_token
}

resource "aws_codebuild_project" "contact_tracking" {
  name           = "contact_tracking"
  description    = "contact_tracing_project"
  build_timeout  = "5"
  queued_timeout = "5"
  service_role   = aws_iam_role.code_build_iam.arn
  badge_enabled  = "true"

  artifacts {
    type = "NO_ARTIFACTS"
  }

  environment {
    compute_type                = "BUILD_GENERAL1_SMALL"
    image                       = "aws/codebuild/amazonlinux2-x86_64-standard:3.0"
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"
  }

  logs_config {
    cloudwatch_logs {
      status      = "ENABLED"
      group_name  = "project-contact-tracing"
      stream_name = "build-pipeline"
    }
  }

  source {
    type            = "GITHUB_ENTERPRISE"
    location        = "https://${var.github_username}@github.com/CCBDA-UPC/2020_Project_Fri_9_00.git"
    git_clone_depth = 1

    git_submodules_config {
      fetch_submodules = true
    }
  }

  source_version = "master"
}