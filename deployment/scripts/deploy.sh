#!/bin/bash
set -e

# Default values
ENV="staging"
CHART_PATH="../helm"

# Parse command-line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -e|--env) ENV="$2"; shift ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

echo "Deploying to environment: $ENV"

# Use environment-specific values files
HELM_CMD="helm upgrade --install quantacirc-release $CHART_PATH --namespace quantacirc-$ENV -f $CHART_PATH/values.yaml -f $CHART_PATH/values-$ENV.yaml --create-namespace"

echo "Running Helm command: $HELM_CMD"
$HELM_CMD

echo "Deployment successful."
