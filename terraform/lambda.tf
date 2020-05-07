locals {
  lambda_source_file = "lambda_package.zip"
}

data "archive_file" "package_lambda" {
  type        = "zip"
  source_file = "${path.module}/lambda_package/lambda_function.py"
  output_path = "${path.module}/${local.lambda_source_file}"
}

resource "aws_s3_bucket" "lambda" {
  bucket = "contact-tracking-project-2020-lambda"
}


resource "aws_s3_bucket_object" "lambda_code" {
  bucket = aws_s3_bucket.lambda.bucket
  key    = local.lambda_source_file
  source = local.lambda_source_file
  etag = filemd5(local.lambda_source_file)
  depends_on = [data.archive_file.package_lambda]
}

resource "aws_lambda_function" "lambda_package" {
  function_name = "python_lambda"

  # The bucket name as created earlier with "aws s3api create-bucket"
  s3_bucket = aws_s3_bucket.lambda.bucket
  s3_key    = local.lambda_source_file

  # "main" is the filename within the zip file (main.js) and "handler"
  # is the name of the property under which the handler function was
  # exported in that file.
  handler = "lambda_function.lambda_handler"
  runtime = "python3.8"
  role = aws_iam_role.lambda_exec.arn
  depends_on = [aws_s3_bucket.lambda, aws_s3_bucket_object.lambda_code]
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
resource "aws_api_gateway_resource" "proxy" {
  rest_api_id = aws_api_gateway_rest_api.rest_api.id
  parent_id   = aws_api_gateway_rest_api.rest_api.root_resource_id
  path_part   = "{proxy+}"
}

resource "aws_api_gateway_method" "proxy" {
  rest_api_id   = aws_api_gateway_rest_api.rest_api.id
  resource_id   = aws_api_gateway_resource.proxy.id
  http_method   = "ANY"
  authorization = "NONE"
}
resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda_package.function_name
  principal     = "apigateway.amazonaws.com"

  # The "/*/*" portion grants access from any method on any resource
  # within the API Gateway REST API.
  source_arn = "${aws_api_gateway_rest_api.rest_api.execution_arn}/*/*"
}