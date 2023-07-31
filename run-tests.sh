#!/bin/bash
PY=${PWD}/tmp.venv/bin/python3


for tool in \
    colour_text \
    colour_filter \
    ssh_wait \
    smart_find \
    ;
do
    if ${tool}/run-test.sh ${PY}
    then
        "${PY}" -m colour_text "<>green PASSED<> ${PY} ${tool}"
    else
        "${PY}" -m colour_text "<>red FAILED<> ${PY} ${tool}"
    fi
done
