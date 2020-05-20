#!/usr/bin/bash
#Script for Deployment
#Lambda deployment
export AWS_PAGER=""
lambda_function=launch_simulation
pushd aws_lambda
aws lambda update-function-code --function-name=$lambda_function --zip-file=fileb://lambda_artifact.zip --output json
aws lambda publish-version --function-name $lambda_function --output json
popd

#Frontend Deployment
pushd frontend
aws s3 cp build/ s3://cc-project-2020-fe --recursive
popd

#Simulator Deployment
pushd simulator
aws s3 cp . s3://cc-project-simulation-app --recursive
popd