#!/bin/bash

# clean up build artifacts
rm -rf dist build

for tool in \
    colour_print \
    ssh_wait \
    ;
do
    python3.7 setup_${tool}.py sdist bdist_wheel
done

ls -l dist/*.whl
