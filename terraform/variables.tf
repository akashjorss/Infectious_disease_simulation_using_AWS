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

variable "aws_region" {
  default     = "eu-west-1"
  type        = string
}