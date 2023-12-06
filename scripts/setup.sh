#!/usr/bin/env bash
# Setup basic software dependencies for developing this blog
#
set -euo pipefail

if ! command -v brew &> /dev/null
then
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    brew update
fi

# setup kubectl
if ! command -v kubectl &> /dev/null
then
    brew install kubectl
fi

if ! command -v helm &> /dev/null
then
    brew install helm
fi

# setup kind
if ! command -v kind &> /dev/null
then
    brew install kind
fi

# setup a kind cluster
CLUSTER_NAME=thetofu

(kind get clusters|grep "${CLUSTER_NAME}") ||kind create cluster --name "${CLUSTER_NAME}"

kubectl cluster-info --context "kind-${CLUSTER_NAME}"

kubectl config use-context "kind-${CLUSTER_NAME}"

# we should use argocd
helm repo add \
crossplane-stable https://charts.crossplane.io/stable
helm repo update

helm install crossplane \
crossplane-stable/crossplane \
--dry-run --debug \
--namespace crossplane-system \
--create-namespace

helm install crossplane \
crossplane-stable/crossplane \
--namespace crossplane-system \
--create-namespace


kubectl get pods -n crossplane-system

kubectl api-resources  | grep crossplane

