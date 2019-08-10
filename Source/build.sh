#!/bin/bash
set -e

PY=python3.7

# clean up build artifacts
rm -rf dist build

for tool in \
    colour_print \
    ssh_wait \
    smart_find \
    ;
do
    ${PY} -m colour_print "~green Info:~ building ~yellow %s~" ${tool}
    ${PY} setup_${tool}.py --quiet sdist bdist_wheel
done

${PY} -m colour_print "~green Info:~ twine check"
${PY} -m twine check dist/*

${PY} -m colour_print "~green Info:~ Built wheels"
ls -l dist/*.whl
