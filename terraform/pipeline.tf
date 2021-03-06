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
locals {
  code_build_project_name = "contact_tracking"
}
data "aws_iam_policy_document" "code_build_policy" {
  version = "2012-10-17"
  statement {
    sid    = "LogPermission"
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
    "logs:PutLogEvents"]
    resources = [
    "*"]
  }
  statement {
    sid    = "ComputePermission"
    effect = "Allow"
    actions = [
      "ec2:CreateNetworkInterface",
      "ec2:DescribeDhcpOptions",
      "ec2:DescribeNetworkInterfaces",
      "ec2:DeleteNetworkInterface",
      "ec2:DescribeSubnets",
      "ec2:DescribeSecurityGroups",
    "ec2:DescribeVpcs"]
    resources = [
      "arn:aws:logs:${data.aws_region.region.name}:${data.aws_caller_identity.current.account_id}:log-group:${local.code_build_project_name}",
    "arn:aws:logs:${data.aws_region.region.name}:${data.aws_caller_identity.current.account_id}:log-group:${local.code_build_project_name}:*"]
  }
  statement {
    sid    = "NetworkPermission"
    effect = "Allow"
    actions = [
    "ec2:CreateNetworkInterfacePermission"]
    resources = [
      "arn:aws:ec2:${data.aws_region.region.name}:${data.aws_caller_identity.current.account_id}:network-interface/*"
    ]
  }
  statement {
    sid    = "LambdaDeploymentPermission"
    effect = "Allow"
    actions = [
      "lambda:UpdateFunctionCode",
    "lambda:PublishVersion"]
    resources = [
      "arn:aws:lambda:${data.aws_region.region.name}:${data.aws_caller_identity.current.account_id}:function",
      "arn:aws:lambda:${data.aws_region.region.name}:${data.aws_caller_identity.current.account_id}:function:*"
    ]
  }

  statement {
    sid    = "S3Deployment"
    effect = "Allow"
    actions = [
      "s3:PutObject",
      "s3:GetObject",
      "s3:GetObjectVersion",
      "s3:GetBucketAcl",
    "s3:GetBucketLocation"]
    resources = [
      "arn:aws:s3:::${aws_s3_bucket.fe_s3.bucket}/*",
    "arn:aws:s3:::${aws_s3_bucket.simulation_spark.bucket}/*"]
  }
}

resource "aws_iam_role_policy" "code_build_iam_policy" {
  role   = aws_iam_role.code_build_iam.name
  policy = data.aws_iam_policy_document.code_build_policy.json
}

resource "aws_codebuild_source_credential" "github_access_token" {
  auth_type   = "PERSONAL_ACCESS_TOKEN"
  server_type = "GITHUB_ENTERPRISE"
  token       = var.github_personal_token
}

resource "aws_codebuild_project" "contact_tracking" {
  name           = local.code_build_project_name
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

  cache {
    type = "LOCAL"
    modes = [
    "LOCAL_CUSTOM_CACHE"]
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