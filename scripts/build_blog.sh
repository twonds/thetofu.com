#!/usr/bin/env bash
#
# Generate blog application using reflex.dev
#
#
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
PROJECT_NAME="${1:-reflexdocs}"
TEAR_DOWN="${2}"

set -euo pipefail



"${SCRIPT_DIR}"/init.sh "${PROJECT_NAME}"


if [ -n "${TEAR_DOWN}" ]
then
"${SCRIPT_DIR}/destroy.sh ${PROJECT_NAME}"
fi
