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

variable "cognito_signout_url" {
  default     = "https://www.localhost/signout"
  type        = string
  description = "Callback URL for logging out client"
}