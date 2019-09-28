#!/bin/bash
for PY in python3.7 python2.7
do
    ${PY} -m colour_text "<>green Info:<> Installing wheels for ${PY}"
    d=$(pwd)
    pushd ${TMPDIR}
    # cannot install from the source dir
    ${PY} -m pip install --upgrade --user --no-warn-script-location ${d}/dist/*.whl
    popd
done
