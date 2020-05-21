resource "aws_s3_bucket" "simulation_spark" {
  bucket = "${data.aws_caller_identity.current.account_id}-cc-project-simulation-app"
  acl    = "private"
}

resource "aws_s3_bucket" "simulation_spark_logs" {
  bucket = "${data.aws_caller_identity.current.account_id}-cc-project-simulation-app-logs"
  acl    = "private"
}