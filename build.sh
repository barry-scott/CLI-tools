#!/bin/bash
set -e

echo "Info: Creating venv..."
rm -rf tmp.venv

/usr/bin/python3 -m venv tmp.venv --upgrade-deps

echo "Info: Installing build tools into venv..."
PY=${PWD}/tmp.venv/bin/python
tmp.venv/bin/python -m pip install --quiet  \
    setuptools build twine \
    mypy \
    colour-text

echo "Info: Building..."

# clean up build artifacts
rm -rf dist build

function build_tool {
    ${PY} -m colour_text "<>green Info:<> building <>yellow %s<>" ${1}
    # setup tools insists on finding the README.md in the current folder
    pushd ${1}
    if [[ -e requirements.txt ]]
    then
        ${PY} -m pip install --requirement ./requirements.txt
    fi
    cd src
    echo ${PY} -m mypy ${1}
    cd ..
    ${PY} -m colour_text "<>green Info:<> build $1"
    ${PY} -m build
    ${PY} -m colour_text "<>green Info:<> twine check"
    ${PY} -m twine check dist/*
    popd
}

if [[ "$1" = "" ]]
then
    build_tool colour_text
    build_tool colour_filter
    build_tool ssh_wait
    build_tool smart_find
    build_tool update_linux

else
    build_tool "${1:?tool name}"
fi

${PY} -m colour_text "<>green Info:<> Built wheels"
ls -l */dist/*.whl
