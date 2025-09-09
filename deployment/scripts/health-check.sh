#!/bin/bash
set -e

# Default values
ENV="staging"
RELEASE_NAME="quantacirc-release"

# Parse command-line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -e|--env) ENV="$2"; shift ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

echo "Checking health of environment: $ENV"

# Check the status of the Helm release
helm status $RELEASE_NAME --namespace quantacirc-$ENV

# Check the rollout status of deployments
for deploy in $(kubectl get deployments -n quantacirc-$ENV -o jsonpath='{.items[*].metadata.name}'); do
  echo "Checking deployment: $deploy"
  kubectl rollout status deployment/$deploy -n quantacirc-$ENV
done

echo "Health check complete. All deployments are rolled out successfully."
