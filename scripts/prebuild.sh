#!/usr/bin/bash
set -e
set -x

python --version
# Test inside virtualenv to not break AWS CLI
python -m venv /tmp/cc_project_python/venv
echo "Created VirtualEnv"
source /tmp/cc_project_python/venv/bin/activate
echo "Activated VirtualEnv"
pip install -r requirements.txt
pytest
deactivate
echo "Deactivated VirtualEnv"


# Frontend dependencies
pushd frontend
npm install
popd