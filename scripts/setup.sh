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

# setup argo cli
if ! command -v argo &> /dev/null
then
    brew install argo
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

helm upgrade -i crossplane \
crossplane-stable/crossplane \
--dry-run --debug \
--namespace crossplane-system \
--create-namespace

helm upgrade -i crossplane \
crossplane-stable/crossplane \
--namespace crossplane-system \
--create-namespace

sleep 1
echo "Waiting on crossplane to start..."
kubectl wait --for=condition=ready pod -l app=crossplane -n crossplane-system

kubectl get pods -n crossplane-system

kubectl api-resources  | grep crossplane
echo "Installing Argo workflows"
kubectl create namespace argo || echo
kubectl apply -n argo -f https://github.com/argoproj/argo-workflows/releases/download/v3.5.2/install.yaml

# bypass the UI login for now
kubectl patch deployment \
  argo-server \
  --namespace argo \
  --type='json' \
  -p='[{"op": "replace", "path": "/spec/template/spec/containers/0/args", "value": [
  "server",
  "--auth-mode=server"
]}]'

# Open a port to the argo UI
# kubectl -n argo port-forward deployment/argo-server 2746:2746

kubectl create rolebinding default-admin --clusterrole=admin --serviceaccount=argo:default --namespace=argo

# kubectl crossplane install provider crossplanecontrib/provider-kubernetes:v0.9.0
kubectl apply -f argo/k8s-provider.yaml

# What provider do we need?
