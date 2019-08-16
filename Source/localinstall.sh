#!/bin/bash
for PY in python3.7 python2.7
do
    ${PY} -m colour_text "<>green Info:<> Installing wheels for ${PY}"
    ${PY} -m pip install --upgrade --user dist/*.whl
done
