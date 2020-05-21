#!/bin/bash
sudo yum update -y
sudo pip3 install --upgrade pip
python3 -m pip install --upgrade setuptools wheel pip
mkdir -p ~/app
cd ~/app || exit
aws s3 cp s3://311807373494-cc-project-simulation-app . --recursive
python3 -m pip --no-cache-dir install -r requirements.txt
