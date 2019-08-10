#!/bin/bash
for tool in \
    cprint \
    ;
do
    python3.7 setup_${tool}.py sdist bdist_wheel
done

ls -l dist/*.whl
