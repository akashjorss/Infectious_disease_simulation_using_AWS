provider "aws" {
  version = "~> 2.60"
}

provider "archive" {
  version = "~> 1.3"
}

data "aws_caller_identity" "current" {}

data "aws_region" "region" {}