import json
import logging
import os
import traceback
import uuid
from typing import Dict

import boto3

try:
    # Assume we're a sub-module in a package.
    from . import utils
except ImportError:
    # Apparently no higher-level package has been imported, fall back to a local import.
    import utils

SUB = "sub"

if len(logging.getLogger().handlers) > 0:
    # The Lambda environment pre-configures a handler logging to stderr. If a handler is already configured,
    # `.basicConfig` does not execute. Thus we set the level directly.
    logging.getLogger().setLevel(logging.INFO)
else:
    logging.basicConfig(level=logging.INFO)

ssm_client = boto3.client("ssm", region_name="us-east-1")
emr_client = boto3.client("emr", region_name="us-east-1")
app_config_path = os.environ["APP_CONFIG_PATH"]
full_config_path = "/" + app_config_path
# Initialize app at global scope for reuse across invocations
app = None


class SimulationLauncher:
    simulation_app: str
    log_path: str
    bootstrap_script_path: str
    instance_type: str

    def __init__(self, ssm_parameter_path):
        """
        Construct new SimulationLauncher with configuration
        :param config: application configuration
        """
        config_dict = {}
        try:
            # Get all parameters for this app
            param_details = ssm_client.get_parameters_by_path(
                Path=ssm_parameter_path, Recursive=False, WithDecryption=True
            )

            # Loop through the returned parameters and populate the ConfigParser
            if "Parameters" in param_details and len(param_details.get("Parameters")) > 0:
                for param in param_details.get("Parameters"):
                    param_path_array = param.get("Name").split("/")
                    section_position = len(param_path_array) - 1
                    section_name = param_path_array[section_position]
                    config_values = param.get("Value")
                    config_dict[section_name] = config_values
                    logging.info("Found configuration: " + str(config_dict))

        except:
            print("Encountered an error loading config from SSM.")
            traceback.print_exc()
        self.simulation_app = config_dict["simulation_app"]
        self.simulation_app = config_dict["log_path"]
        self.bootstrap_script_path = config_dict["bootstrap_script_path"]
        self.instance_type = config_dict["instance_type"]


def lambda_handler(event, context):
    global app
    # Initialize app if it doesn't yet exist
    if app is None:
        logging.info("Loading config and creating new SimulationLauncher...")
        app = SimulationLauncher(full_config_path)
    claims = utils.fetch_claims(event)
    user_id = claims[SUB]
    logging.info(f"Running Simulation for subject {user_id}")
    simulation_id = str(uuid.uuid4())
    logging.info(f"Generated Simulation ID for this run is {simulation_id}")
    response = create_emr(simulation_id, user_id)
    logging.info(f"Cluster ARN and JobID ${json.dumps(response)}")
    return {
        "statusCode": 200,
        "headers": {"Access-Control-Allow-Origin": "*"},
        "body": json.dumps({"simulation_id": simulation_id}),
    }


def create_emr(simulation_id: str, user_id: str) -> Dict[str, str]:
    global app
    disk_config = {
        "EbsBlockDeviceConfigs": [
            {"VolumeSpecification": {"VolumeType": "gp2", "SizeInGB": 10}, "VolumesPerInstance": 1},
        ],
        "EbsOptimized": False,
    }
    response = emr_client.run_job_flow(
        Name=simulation_id,
        ReleaseLabel="emr-6.0.0",
        LogUri=app.log_path,
        Instances={
            "InstanceGroups": [
                {
                    "Name": "Master-1",
                    "Market": "ON_DEMAND",
                    "InstanceRole": "MASTER",
                    "InstanceType": app.instance_type,
                    "InstanceCount": 1,
                    "EbsConfiguration": disk_config,
                },
                {
                    "Name": "Core-1",
                    "Market": "ON_DEMAND",
                    "InstanceRole": "CORE",
                    "InstanceType": app.instance_type,
                    "InstanceCount": 1,
                    "EbsConfiguration": disk_config,
                },
                {
                    "Name": "Auto Scaling Group",
                    "Market": "SPOT",
                    "InstanceRole": "TASK",
                    "InstanceType": app.instance_type,
                    "InstanceCount": 1,
                    "EbsConfiguration": disk_config,
                    "AutoScalingPolicy": {
                        "Constraints": {"MinCapacity": 0, "MaxCapacity": 10},
                        "Rules": [
                            {
                                "Name": "Scale Out",
                                "Description": "Rules for scaling out EMR",
                                "Action": {
                                    "SimpleScalingPolicyConfiguration": {
                                        "AdjustmentType": "CHANGE_IN_CAPACITY",
                                        "ScalingAdjustment": 2,
                                        "CoolDown": 60,
                                    },
                                },
                                "Trigger": {
                                    "CloudWatchAlarmDefinition": {
                                        "ComparisonOperator": "LESS_THAN",
                                        "EvaluationPeriods": 1,
                                        "MetricName": "YARNMemoryAvailablePercentage",
                                        "Namespace": "AWS/ElasticMapReduce",
                                        "Period": 300,
                                        "Statistic": "AVERAGE",
                                        "Threshold": 25,
                                        "Unit": "PERCENT",
                                        "Dimensions": [{"Key": "JobFlowId", "Value": "${emr.clusterId}"},],
                                    }
                                },
                            },
                        ],
                    },
                },
            ],
            "KeepJobFlowAliveWhenNoSteps": False,
            "TerminationProtected": False,
        },
        Steps=[
            {
                "Name": "simulation",
                "ActionOnFailure": "TERMINATE_CLUSTER",
                "HadoopJarStep": {
                    "Jar": "command-runner.jar",
                    "Args": [
                        "/usr/bin/spark-submit",
                        "--verbose",
                        "--deploy-mode",
                        "cluster",
                        "--master",
                        "yarn",
                        app.simulation_app,
                    ],
                },
            },
        ],
        BootstrapActions=[
            {"Name": "Setup cluster", "ScriptBootstrapAction": {"Path": app.bootstrap_script_path, "Args": []}}
        ],
        Applications=[{"Name": "Spark"}],
        Configurations=[
            {
                "Classification": "spark-env",
                "Configurations": [{"Classification": "export", "Properties": {"PYSPARK_PYTHON": "/usr/bin/python3"}}],
            }
        ],
        VisibleToAllUsers=True,
        JobFlowRole="EMR_EC2_DefaultRole",
        ServiceRole="EMR_DefaultRole",
        AutoScalingRole="EMR_AutoScaling_DefaultRole",
        Tags=[{"Key": "user", "Value": user_id}],
    )
    return response


# create_emr("b777d642-beac-48c6-8618-080001952041", "88ac8d98-c594-4c8d-b6d5-95442910554b")

if __name__ == "__main__":
    if app is None:
        logging.info("Loading config and creating new SimulationLauncher...")
        app = SimulationLauncher("/simulation_lambda")
