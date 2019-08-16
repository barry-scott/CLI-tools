#!/bin/bash
set -e

PY=python3.7

# clean up build artifacts
rm -rf dist build

function build_tool {
    ${PY} -m colour_text "<>green Info:<> building <>yellow %s<>" ${1}
    # setup tools insists on finding the README.md in the current folder
    cp -f ${1}/README.md .
    ${PY} setup_${1}.py --quiet sdist bdist_wheel
    rm -f README.md
}

if [[ "$1" = "" ]]
then
    for tool in \
        colour_text \
        colour_filter \
        ssh_wait \
        smart_find \
        ;
    do
        build_tool "${tool}"
    done

else
    build_tool "${1}"
fi


${PY} -m colour_text "<>green Info:<> twine check"
${PY} -m twine check dist/*

${PY} -m colour_text "<>green Info:<> Built wheels"
ls -l dist/*.whl
