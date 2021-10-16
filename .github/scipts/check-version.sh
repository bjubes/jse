#!/bin/bash

EXEC_VER=$(./run.py --version | awk '{print $3'})
PYPI_VER=$(poetry version | awk '{print $2'})

[[ "$EXEC_VER" == "$PYPI_VER" ]] && echo "PyPi and Executable versions match" && exit 0;
echo "Pypi version: $PYPI_VER"
echo "Executable version: $EXEC_VER"
echo "Version mismatch"
exit 1;