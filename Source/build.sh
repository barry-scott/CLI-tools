#!/bin/bash
set -e

PY=python3.7

# clean up build artifacts
rm -rf dist build

for tool in \
    colour_text \
    colour_filter \
    ssh_wait \
    smart_find \
    ;
do
    ${PY} -m colour_text "~green Info:~ building ~yellow %s~" ${tool}
    # setup tools insists on finding the README.md in the current folder
    cp -f $tool/README.md .
    ${PY} setup_${tool}.py --quiet sdist bdist_wheel
done

rm -f README.md

${PY} -m colour_text "~green Info:~ twine check"
${PY} -m twine check dist/*

${PY} -m colour_text "~green Info:~ Built wheels"
ls -l dist/*.whl
