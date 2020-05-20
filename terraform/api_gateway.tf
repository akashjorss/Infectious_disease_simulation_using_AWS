resource "aws_api_gateway_rest_api" "rest_api" {
  name        = "api_gateway_rest"
  description = "Terraform Serverless Application"
  endpoint_configuration {
    types = [
    "REGIONAL"]
  }
}

resource "aws_api_gateway_resource" "simulation_root" {
  rest_api_id = aws_api_gateway_rest_api.rest_api.id
  parent_id   = aws_api_gateway_rest_api.rest_api.root_resource_id
  path_part   = "simulate"
}

resource "aws_api_gateway_method" "emr_lambda_options" {
  rest_api_id   = aws_api_gateway_rest_api.rest_api.id
  resource_id   = aws_api_gateway_resource.simulation_root.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_method_response" "options_200" {
  rest_api_id = aws_api_gateway_rest_api.rest_api.id
  resource_id = aws_api_gateway_resource.simulation_root.id
  http_method = aws_api_gateway_method.emr_lambda_options.http_method
  status_code = 200
  response_models = {
    "application/json" = "Empty"
  }
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true,
    "method.response.header.Access-Control-Allow-Methods" = true,
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
  depends_on = [
  aws_api_gateway_method.emr_lambda_options]
}

resource "aws_api_gateway_integration" "options_integration" {
  rest_api_id = aws_api_gateway_rest_api.rest_api.id
  resource_id = aws_api_gateway_resource.simulation_root.id
  http_method = aws_api_gateway_method.emr_lambda_options.http_method
  type        = "MOCK"
  request_templates = {
    "application/json" = jsonencode(
      {
        statusCode = 200
      }
    )
  }
  depends_on = [
  aws_api_gateway_method.emr_lambda_options]
}

resource "aws_api_gateway_integration_response" "options_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.rest_api.id
  resource_id = aws_api_gateway_resource.simulation_root.id
  http_method = aws_api_gateway_method.emr_lambda_options.http_method
  status_code = aws_api_gateway_method_response.options_200.status_code
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
    "method.response.header.Access-Control-Allow-Methods" = "'GET,OPTIONS,POST,PUT'",
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
  depends_on = [
  aws_api_gateway_method_response.options_200]
}

resource "aws_api_gateway_method_response" "cors_method_response_200" {
  rest_api_id = aws_api_gateway_rest_api.rest_api.id
  resource_id = aws_api_gateway_resource.simulation_root.id
  http_method = aws_api_gateway_method.emr_lambda.http_method
  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = true
  }
  depends_on = [
  aws_api_gateway_method.emr_lambda]
  status_code = 200
}

resource "aws_api_gateway_method" "emr_lambda" {
  rest_api_id   = aws_api_gateway_rest_api.rest_api.id
  resource_id   = aws_api_gateway_resource.simulation_root.id
  http_method   = "POST"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.cognito_authorizer.id
}

resource "aws_api_gateway_integration" "lambda" {
  rest_api_id = aws_api_gateway_rest_api.rest_api.id
  resource_id = aws_api_gateway_method.emr_lambda.resource_id
  http_method = aws_api_gateway_method.emr_lambda.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.launch_simulation.invoke_arn
}

resource "aws_api_gateway_deployment" "gateway_deployment" {
  depends_on = [
    aws_api_gateway_integration.lambda, aws_api_gateway_integration.options_integration
  ]

  rest_api_id = aws_api_gateway_rest_api.rest_api.id
  stage_name  = "test"
}

resource "aws_api_gateway_authorizer" "cognito_authorizer" {
  name        = "cognito_authorizer_cc_project"
  rest_api_id = aws_api_gateway_rest_api.rest_api.id
  type        = "COGNITO_USER_POOLS"
  provider_arns = [
  aws_cognito_user_pool.cc-pool.arn]
}