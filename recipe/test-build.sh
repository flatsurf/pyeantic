#!/bin/bash
set -eo pipefail

# Check that the tests actually pass before we attempt to profile them
make check || (cat `find -name test-suite.log`; false)

# Finally some static checks
LD_LIBRARY_PATH="$PREFIX/lib:$LD_LIBRARY_PATH" ./recipe/build-distcheck.sh
./recipe/build-todo.sh
