#!/bin/bash

# Prepare archive requests dependency
./package_function.sh

# Deploy to Lambda
aws lambda update-function-code --function-name grafana-env --zip-file fileb://function.zip
