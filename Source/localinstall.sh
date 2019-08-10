#!/bin/bash
PY=python3.7

${PY} -m colour_print "~green Info:~ Installing wheels"
python3.7 -m pip install --upgrade --user dist/*.whl
