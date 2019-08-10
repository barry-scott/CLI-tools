#!/bin/bash

# clean up build artifacts
rm -rf dist build

for tool in \
    colour_print \
    ssh_wait \
    smart_find \
    ;
do
    python3.7 -m colour_print "~green Info:~ building ~yellow %s~" ${tool}
    python3.7 setup_${tool}.py --quiet sdist bdist_wheel
done

ls -l dist/*.whl
