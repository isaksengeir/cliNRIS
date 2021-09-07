#!/usr/bin/env bash

export PIP_REQUIRE_VIRTUALENV=true

python -m venv venv

source venv/bin/activate

python -m pip install --upgrade pip

pip install -r requirements.txt

