#!/bin/bash

# Run sudo apt-get install libasound2-dev
# Run sudo apt-get install libjack-dev

virtualenv env -p python3.8
source env/bin/activate
pip install -e .
