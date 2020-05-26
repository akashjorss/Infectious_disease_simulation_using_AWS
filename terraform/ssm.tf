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


locals {
  spark_es_params = [
    "cloud_id",
    "username",
  "password"]
}

locals {
  spark_simulation_app = "spark_simulation_app"
}

resource "aws_kms_key" "es_secret_key" {
  description             = "Key for encrypting ES credentials for use in "
  deletion_window_in_days = 7
}



resource "aws_ssm_parameter" "simulation_spark_secure_params" {
  count  = length(local.spark_es_params)
  name   = "/${local.spark_simulation_app}/${local.spark_es_params[count.index]}"
  type   = "SecureString"
  value  = "default"
  key_id = aws_kms_key.es_secret_key.key_id
  lifecycle {
    ignore_changes = [
      value,
    version]
  }
}