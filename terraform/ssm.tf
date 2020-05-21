locals {
  simulation_app = "simulation_lambda"
}

locals {
  simulation_app_params = [
    "simulation_app",
    "log_path",
    "bootstrap_script_path",
  "instance_type"]
}

resource "aws_ssm_parameter" "simulation_lambda_params" {
  count = length(local.simulation_app_params)
  name  = "/${local.simulation_app}/${local.simulation_app_params[count.index]}"
  type  = "String"
  value = "default"
  lifecycle {
    ignore_changes = [
      value,
    version]
  }
}