#!/usr/bin/env bash
#
# Generate blog application using reflex.dev
#
#
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
PROJECT_NAME="${1:-reflexdocs}"
TEAR_DOWN="${2}"

set -euo pipefail


#The reflex init command creates a new Reflex app in the current directory. If a rxconfig.py file already exists already, it will re-initialize the app with the latest template.
# XXX - What minimum code do we need?
# XXX - Can we use an outside template on init? How about downloading from github?
# https://github.com/reflex-dev/reflex/blob/6e1bce341288758972229772e664622604b4dfd5/reflex/constants/base.py#L77
"${SCRIPT_DIR}"/init.sh "${PROJECT_NAME}"


cd "${PROJECT_NAME}"
ls -la
reflex run &
echo "$!" > ./reflex.pid

open "http://localhost:3000"

# Generate or copy pages

# XXX - when deploying how do we make things composable and still use k8s?
# XXX - how do we make everything gitops too?
# XXX - do we build docker images locally or everything remotely?

if [ -n "${TEAR_DOWN}" ]
then
"${SCRIPT_DIR}/destroy.sh ${PROJECT_NAME}"
fi
