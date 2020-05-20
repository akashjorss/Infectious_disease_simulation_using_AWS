resource "aws_s3_bucket" "simulation_spark" {
  bucket = "cc-project-simulation-app"
  acl    = "private"
}

resource "aws_s3_bucket" "simulation_spark_logs" {
  bucket = "cc-project-simulation-app-logs"
  acl    = "private"
}