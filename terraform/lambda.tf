locals {
  lambda_source_file = "lambda_package.zip"
}

resource "aws_lambda_function" "launch_simulation" {
  function_name = "launch_simulation"

  filename = "${path.module}/${local.lambda_source_file}"

  handler = "launch_simulation.lambda_handler"
  runtime = "python3.8"
  publish = true
  role    = aws_iam_role.lambda_exec.arn
  //  Code deployed from CI / CD
  lifecycle {
    ignore_changes = [
      filename,
    source_code_hash]
  }
}

# IAM role which dictates what other AWS services the Lambda function
# may access.
resource "aws_iam_role" "lambda_exec" {
  name               = "lambda_role"
  assume_role_policy = <<EOF
{
"Version": "2012-10-17",
"Statement": [
{
"Action": "sts:AssumeRole",
"Principal": {
"Service": "lambda.amazonaws.com"
},
"Effect": "Allow",
"Sid": ""
}
]
}
EOF
}

data "aws_iam_policy_document" "iam_policy_for_lambda" {
  statement {
    sid    = "LambdaPolicy"
    effect = "Allow"
    actions = [
      "cloudwatch:PutMetricData",
      "ec2:DescribeNetworkInterfaces",
      "ec2:CreateNetworkInterface",
      "ec2:DeleteNetworkInterface",
      "logs:CreateLogStream",
      "logs:CreateLogGroup",
      "logs:PutLogEvents",
      "xray:PutTelemetryRecords",
      "xray:PutTraceSegments",
      "elasticmapreduce:RunJobFlow",
    "iam:PassRole"]
    resources = [
    "*"]
  }
}

resource "aws_iam_policy" "iam_policy_for_lambda" {
  name   = "lambda-invoke-policy"
  path   = "/"
  policy = data.aws_iam_policy_document.iam_policy_for_lambda.json
}

# Attach the policy to the role
resource "aws_iam_role_policy_attachment" "aws_iam_role_policy_attachment" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = aws_iam_policy.iam_policy_for_lambda.arn
}

resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.launch_simulation.function_name
  principal     = "apigateway.amazonaws.com"

  # The "/*/*" portion grants access from any method on any resource
  # within the API Gateway REST API.
  source_arn = "${aws_api_gateway_rest_api.rest_api.execution_arn}/*/*"
}