#!/usr/bin/bash

set -e
set -x

#Lambda build step
pushd aws_lambda
zip -r lambda_artifact.zip .
popd
#Front end build step
pushd frontend
npm run-script build
popd
#Simulation App
pushd simulator
echo "Build Step for Simulator"
popd