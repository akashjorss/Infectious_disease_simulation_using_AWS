import json
import logging
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

SIMULATION_APP = "s3://cc-project-simulation-app/wordcount.py"
LOGS = "s3://cc-project-simulation-app-logs"
BOOTSTRAP_SCRIPT = "s3://cc-project-simulation-app/bootstrap.sh"

INSTANCE_TYPE = "c4.xlarge"


def lambda_handler(event, context):
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
    client = boto3.client("emr", region_name="us-east-1")
    disk_config = {
        "EbsBlockDeviceConfigs": [
            {"VolumeSpecification": {"VolumeType": "gp2", "SizeInGB": 10}, "VolumesPerInstance": 1},
        ],
        "EbsOptimized": False,
    }
    response = client.run_job_flow(
        Name=simulation_id,
        ReleaseLabel="emr-6.0.0",
        LogUri=LOGS,
        Instances={
            "InstanceGroups": [
                {
                    "Name": "Master-1",
                    "Market": "ON_DEMAND",
                    "InstanceRole": "MASTER",
                    "InstanceType": INSTANCE_TYPE,
                    "InstanceCount": 1,
                    "EbsConfiguration": disk_config,
                },
                {
                    "Name": "Core-1",
                    "Market": "ON_DEMAND",
                    "InstanceRole": "CORE",
                    "InstanceType": INSTANCE_TYPE,
                    "InstanceCount": 1,
                    "EbsConfiguration": disk_config,
                },
                {
                    "Name": "Auto Scaling Group",
                    "Market": "SPOT",
                    "InstanceRole": "TASK",
                    "InstanceType": INSTANCE_TYPE,
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
                        SIMULATION_APP,
                    ],
                },
            },
        ],
        BootstrapActions=[{"Name": "Setup cluster", "ScriptBootstrapAction": {"Path": BOOTSTRAP_SCRIPT, "Args": []}}],
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
