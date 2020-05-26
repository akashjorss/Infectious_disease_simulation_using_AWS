output "code_build_badge_url" {
  value = aws_codebuild_project.contact_tracking.badge_url
}

output "base_url" {
  value = aws_api_gateway_deployment.gateway_deployment.invoke_url
}

output "cognito_hosted_ui" {
  value = "https://${aws_cognito_user_pool_domain.default.domain}.auth.${data.aws_region.region.name}.amazoncognito.com"
}

output "fe_domain" {
  value = aws_cloudfront_distribution.fe_s3_distribution.domain_name
}

output "kibana_client_id" {
  value = aws_cognito_user_pool_client.kibana-project-client.id
}

output "kibana_client_secret" {
  value = aws_cognito_user_pool_client.kibana-project-client.client_secret
}