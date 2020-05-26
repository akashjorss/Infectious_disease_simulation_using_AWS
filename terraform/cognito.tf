resource "aws_cognito_user_pool" "cc-pool" {
  name = "cloud-computing-project-pool"
  admin_create_user_config {
    allow_admin_create_user_only = true
  }
  auto_verified_attributes = [
  "email"]
  password_policy {
    minimum_length    = 6
    require_lowercase = false
    require_numbers   = false
    require_symbols   = false
  }
  username_configuration {
    case_sensitive = false
  }
}

resource "aws_cognito_user_pool_client" "project-client" {
  name                                 = "cloud-computing-project-client"
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_flows = [
  "implicit"]
  allowed_oauth_scopes = [
    "phone",
    "email",
    "openid",
  "profile"]
  user_pool_id           = aws_cognito_user_pool.cc-pool.id
  refresh_token_validity = 30
  callback_urls          = var.cognito_callback_urls
  default_redirect_uri   = var.cognito_callback_urls[0]
  supported_identity_providers = [
  "COGNITO"]
  read_attributes = [
    "address",
    "birthdate",
    "email",
    "email_verified",
    "family_name",
    "gender",
    "given_name",
    "locale",
    "middle_name",
    "name",
    "nickname",
    "phone_number",
    "phone_number_verified",
    "picture",
    "preferred_username",
    "profile",
    "updated_at",
    "website",
    "zoneinfo"
  ]
  write_attributes = [
    "address",
    "birthdate",
    "email",
    "family_name",
    "gender",
    "given_name",
    "locale",
    "middle_name",
    "name",
    "nickname",
    "phone_number",
    "picture",
    "preferred_username",
    "profile",
    "updated_at",
    "website",
    "zoneinfo"
  ]
}

resource "aws_cognito_user_pool_client" "kibana-project-client" {
  name                                 = "kibana-client"
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_flows = [
  "code"]
  allowed_oauth_scopes = [
    "phone",
    "email",
    "openid",
  "profile"]
  user_pool_id           = aws_cognito_user_pool.cc-pool.id
  refresh_token_validity = 30
  callback_urls          = var.kibana_callback_urls
  default_redirect_uri   = var.kibana_callback_urls[0]
  supported_identity_providers = [
  "COGNITO"]
  read_attributes = [
    "address",
    "birthdate",
    "email",
    "email_verified",
    "family_name",
    "gender",
    "given_name",
    "locale",
    "middle_name",
    "name",
    "nickname",
    "phone_number",
    "phone_number_verified",
    "picture",
    "preferred_username",
    "profile",
    "updated_at",
    "website",
    "zoneinfo"
  ]
  write_attributes = [
    "address",
    "birthdate",
    "email",
    "family_name",
    "gender",
    "given_name",
    "locale",
    "middle_name",
    "name",
    "nickname",
    "phone_number",
    "picture",
    "preferred_username",
    "profile",
    "updated_at",
    "website",
    "zoneinfo"
  ]
  generate_secret = true
}

resource "aws_cognito_user_pool_domain" "default" {
  user_pool_id = aws_cognito_user_pool.cc-pool.id
  domain       = "cc-project-2020-fri-9"
}
