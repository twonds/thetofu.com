#!/usr/bin/env bash
# Setup basic software dependencies for developing this blog
#
set -euo pipefail

# For now we setup brew and make the assumption the developer is
# using mac os
if ! command -v brew &> /dev/null
then
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

PYTHON=python

# Check python
if command -v python3 &> /dev/null
then
    PYTHON=python3
fi

if ! command -v "${PYTHON}" &> /dev/null
then
    brew install python3
fi

set -x
# Check for poetry
if ! command -v poetry &> /dev/null
then
    # curl -sSL https://install.python-poetry.org | "${PYTHON}" -
    brew install poetry
fi
