#!/bin/bash
set -e
cat <<EOF | ${1} -m colour_filter info yellow error magenta
info is yellow info
error is magenta and info is yellow
EOF

