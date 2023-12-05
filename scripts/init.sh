#!/usr/bin/env bash
#
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

"${SCRIPT_DIR}/setup.sh"

set -eo pipefail

PROJECT_NAME="${1}"
if [ -z "${PROJECT_NAME}" ]
then
    echo "You MUST provide a project name"
    exit 1
fi

set -u

echo "Initializing ${PROJECT_NAME}"
poetry new "${PROJECT_NAME}"
cd "${PROJECT_NAME}"
reflex init
poetry add dulwich
