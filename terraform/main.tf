provider "aws" {
  version = "~> 2.60"
  region = "eu-west-1"
}

data "aws_caller_identity" "current" {}