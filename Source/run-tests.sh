#!/bin/bash
PY2=python2.7
PY3=python3.7

function cprint {
    "${PY3}" -m colour_text "$@"
}

for tool in \
    colour_text \
    colour_filter \
    ssh_wait \
    smart_find \
    ;
do
    for PY in ${PY3} ${PY2}
    do
        if ${tool}/run-test.sh ${PY}
        then
            cprint "<>green PASSED<> ${PY} ${tool}"
        else
            cprint "<>red FAILED<> ${PY} ${tool}"
        fi
    done
done
