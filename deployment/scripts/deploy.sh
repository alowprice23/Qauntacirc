#!/bin/bash
set -eo pipefail

# --- Configuration ---
DEFAULT_ENV="staging"
CHART_PATH="../helm"
RELEASE_NAME="quantacirc-release"

# --- Helper Functions ---
info() {
  echo "[INFO] $1"
}

error() {
  echo "[ERROR] $1" >&2
  exit 1
}

# --- Argument Parsing ---
ENV=$DEFAULT_ENV
DRY_RUN=false
WAIT=false

while [[ "$#" -gt 0 ]]; do
    case $1 in
        -e|--env) ENV="$2"; shift ;;
        --dry-run) DRY_RUN=true ;;
        --wait) WAIT=true ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

# --- Pre-flight Checks ---
if ! command -v helm &> /dev/null; then
  error "Helm is not installed. Please install Helm to continue."
fi

if [ ! -d "$CHART_PATH" ]; then
    error "Helm chart not found at $CHART_PATH. This script should be run from the deployment/scripts directory."
fi

VALUES_FILE="$CHART_PATH/values-$ENV.yaml"
if [ ! -f "$VALUES_FILE" ]; then
    error "Values file for environment '$ENV' not found at $VALUES_FILE"
fi

# --- Main Script ---
info "Starting deployment to environment: $ENV"
NAMESPACE="quantacirc-$ENV"

HELM_CMD="helm upgrade --install $RELEASE_NAME $CHART_PATH"
HELM_CMD="$HELM_CMD --namespace $NAMESPACE"
HELM_CMD="$HELM_CMD -f $CHART_PATH/values.yaml"
HELM_CMD="$HELM_CMD -f $VALUES_FILE"
HELM_CMD="$HELM_CMD --create-namespace"

if [ "$DRY_RUN" = true ]; then
  HELM_CMD="$HELM_CMD --dry-run"
  info "Performing a dry run. No changes will be applied."
fi

if [ "$WAIT" = true ]; then
  HELM_CMD="$HELM_CMD --wait"
  info "Will wait for all resources to be in a ready state."
fi

info "Executing Helm command:"
echo "$HELM_CMD"
$HELM_CMD

if [ "$DRY_RUN" = false ]; then
  info "Deployment to environment '$ENV' initiated successfully."
  if [ "$WAIT" = true ]; then
    info "All resources are in a ready state."
  fi
else
  info "Dry run completed."
fi
