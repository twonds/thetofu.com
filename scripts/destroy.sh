#!/usr/bin/env bash
# XXX - do not erase or destory git repo for now
#
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
set -euo pipefail

PROJECT_NAME="${1}"
if [ -z "${PROJECT_NAME}" ]
then
    echo "You MUST provide a project name"
    exit 1
fi

rm -rf "${PROJECT_NAME}"
