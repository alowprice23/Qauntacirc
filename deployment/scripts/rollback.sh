#!/bin/bash
set -eo pipefail

# --- Configuration ---
DEFAULT_ENV="staging"
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
REVISION=""
WAIT=false
YES=false

while [[ "$#" -gt 0 ]]; do
    case $1 in
        -e|--env) ENV="$2"; shift ;;
        -r|--revision) REVISION="$2"; shift ;;
        --wait) WAIT=true ;;
        -y|--yes) YES=true ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

# --- Pre-flight Checks ---
if ! command -v helm &> /dev/null; then
  error "Helm is not installed. Please install Helm to continue."
fi
if ! command -v jq &> /dev/null; then
    error "jq is not installed. Please install jq to continue."
fi

# --- Main Script ---
NAMESPACE="quantacirc-$ENV"
info "Checking history for release '$RELEASE_NAME' in namespace '$NAMESPACE'..."

HISTORY=$(helm history $RELEASE_NAME -n $NAMESPACE -o json)
if [ -z "$HISTORY" ] || [ "$(echo $HISTORY | jq 'length')" -le 1 ]; then
    error "No previous revisions found to roll back to."
fi

if [ -z "$REVISION" ]; then
    info "No revision specified. Please select a revision to roll back to:"
    echo "$HISTORY" | jq -r '.[-10:] | .[] | "\(.revision)\t\(.updated)\t\(.status)\t\(.description)"'
    read -p "Enter revision number: " REVISION
fi

if ! echo "$HISTORY" | jq -e ".[] | select(.revision==$REVISION)" > /dev/null; then
    error "Revision '$REVISION' not found in the history."
fi

info "You are about to roll back '$RELEASE_NAME' to revision $REVISION."
if [ "$YES" = false ]; then
    read -p "Are you sure? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        info "Rollback cancelled."
        exit 0
    fi
fi

HELM_CMD="helm rollback $RELEASE_NAME $REVISION -n $NAMESPACE"
if [ "$WAIT" = true ]; then
  HELM_CMD="$HELM_CMD --wait"
  info "Will wait for all resources to be in a ready state after rollback."
fi

info "Executing Helm command:"
echo "$HELM_CMD"
$HELM_CMD

info "Rollback to revision $REVISION completed successfully."
