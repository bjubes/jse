#!/bin/bash

set -e
EXEC_VER=$(./run.py --version | awk '{print $3'})
PYPI_VER=$(poetry version | awk '{print $2'})

if [[ "$EXEC_VER" == "$PYPI_VER" ]]; then
	echo "PyPi and Executable versions match"
	echo "Version: $PYPI_VER"
	exit 0
fi 

echo "Pypi version: $PYPI_VER"
echo "Executable version: $EXEC_VER"
echo "Version mismatch"
exit 1;