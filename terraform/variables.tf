variable "github_personal_token" {
  default     = "github_token"
  type        = string
  description = "Github Personal Access Token"
}

variable "github_username" {
  default     = "default_user"
  type        = string
  description = "Username to use for cloning"
}

variable "cognito_callback_urls" {
  default     = ["https://www.localhost/signin"]
  type        = list(string)
  description = "Callback URLs for client"
}

variable "kibana_callback_urls" {
  default     = ["https://c2f89c43548c40da8c9ade5dae6918e4.us-east-1.aws.found.io:9243/api/security/oidc/callback"]
  type        = list(string)
  description = "Callback URLs Kibana"
}

variable "cognito_signout_url" {
  default     = "https://www.localhost/signout"
  type        = string
  description = "Callback URL for logging out client"
}