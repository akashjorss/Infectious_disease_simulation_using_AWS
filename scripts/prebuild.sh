#!/usr/bin/bash
set -e
pip install -r requirements.txt
pytest
pushd frontend
npm install
popd