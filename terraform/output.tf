output "code_build_badge_url" {
  value = aws_codebuild_project.contact_tracking.badge_url
}

output "base_url" {
  value = aws_api_gateway_deployment.gateway_deployment.invoke_url
}