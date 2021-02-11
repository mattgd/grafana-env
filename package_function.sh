#!/bin/bash

# Download requests dependency
python3 m pip install --target ./package requests

# Add requests to function zip
cd package
zip -r9 ${OLDPWD}/function.zip .

# Add function code to archvive
cd $OLDPWD
zip -g function.zip lambda_function.py grafana_env.py
