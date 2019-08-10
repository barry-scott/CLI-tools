#!/bin/bash
PY=python3.7

${PY} -m colour_text "~green Info:~ Installing wheels"
python3.7 -m pip install --upgrade --user dist/*.whl
