#!/bin/bash
set -e

echo "Info: Creating venv..."
rm -rf tmp.venv

/usr/bin/python3 -m venv tmp.venv

PY=tmp.venv/bin/python
tmp.venv/bin/python -m pip install --quiet \
    setuptools twine wheel \
    colour-text config-path

echo "Info: Building..."

# clean up build artifacts
rm -rf dist build

function build_tool {
    ${PY} -m colour_text "<>green Info:<> building <>yellow %s<>" ${1}
    # setup tools insists on finding the README.md in the current folder
    cp -f ${1}/README.md .
    ${PY} setup_${1}.py --quiet sdist bdist_wheel ${2}
    rm -f README.md
}

if [[ "$1" = "" ]]
then
    build_tool colour_text --universal
    build_tool colour_filter --universal
    build_tool ssh_wait --universal
    build_tool smart_find --universal
    build_tool update_linux --universal

else
    build_tool "${1}" "${2}"
fi

${PY} -m colour_text "<>green Info:<> twine check"
${PY} -m twine check dist/*

${PY} -m colour_text "<>green Info:<> Built wheels"
ls -l dist/*.whl
