locals {
  lambda_source_file = "lambda_package.zip"
}

resource "aws_lambda_function" "launch_simulation" {
  function_name = "launch_simulation"

  filename = "${path.module}/${local.lambda_source_file}"

  handler = "lambda_function.lambda_handler"
  runtime = "python3.8"
  publish = true
  role    = aws_iam_role.lambda_exec.arn
  //  Code deployed from CI / CD
  lifecycle {
    ignore_changes = [filename, source_code_hash]
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

resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.launch_simulation.function_name
  principal     = "apigateway.amazonaws.com"

  # The "/*/*" portion grants access from any method on any resource
  # within the API Gateway REST API.
  source_arn = "${aws_api_gateway_rest_api.rest_api.execution_arn}/*/*"
}