#!/usr/bin/bash
#Script for Deployment
#Lambda deployment
export AWS_PAGER=""
lambda_function=launch_simulation

set -e
set -x

echo "Deploying Lambda"

pushd aws_lambda
aws lambda update-function-code --function-name=$lambda_function --zip-file=fileb://lambda_artifact.zip --output json
aws lambda publish-version --function-name $lambda_function --output json
popd

echo "Deploying Frontend to S3"

#Frontend Deployment
pushd frontend
aws s3 cp build/ s3://311807373494-cc-project-2020-fe --recursive
popd


echo "Deploying Simulator to S3"

#Simulator Deployment
pushd simulator
aws s3 cp . s3://311807373494-cc-project-simulation-app --recursive
popd