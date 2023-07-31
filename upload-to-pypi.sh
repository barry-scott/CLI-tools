#!/bin/bash
set -e
export TWINE_USERNAME=barryscott

tmp.venv/bin/python -m twine check dist/*
tmp.venv/bin/python -m twine upload dist/*
