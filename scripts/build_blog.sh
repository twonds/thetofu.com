#!/usr/bin/env bash
#
# Generate blog application using reflex.dev
#
#
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
PROJECT_NAME="${1}"
TEAR_DOWN="${2}"

set -eo pipefail

if [ -z "${PROJECT_NAME}" ]
then
    echo "You MUST provide a project name"
    exit 1
fi

set -u



"${SCRIPT_DIR}/init.sh ${PROJECT_NAME}"


if [ -n "${PROJECT_NAME}" ]
then
"${SCRIPT_DIR}/destroy.sh ${PROJECT_NAME}"
fi
