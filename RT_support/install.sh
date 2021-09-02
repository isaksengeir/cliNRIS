#!/usr/bin/env bash

export PIP_REQUIRE_VIRTUALENV=true

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt

