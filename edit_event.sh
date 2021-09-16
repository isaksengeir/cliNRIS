#!/usr/bin/env bash

DIRECTORY_THIS_SCRIPT=$( cd "$(dirname "$0")" ; pwd -P )

pysrc="$DIRECTORY_THIS_SCRIPT/RT_support"

. "$pysrc/venv/bin/activate"

export LC_ALL=en_US.utf-8
export LANG=en_US.utf-8

python "$pysrc"/edit_event.py "$@"