#!/bin/bash
set -e

# Default values
ENV="staging"
RELEASE_NAME="quantacirc-release"

# Parse command-line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -e|--env) ENV="$2"; shift ;;
        -r|--revision) REVISION="$2"; shift ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

if [ -z "$REVISION" ]; then
    echo "Getting latest revision..."
    # Get the revision before the current one
    REVISION=$(helm history $RELEASE_NAME --namespace quantacirc-$ENV -o json | jq 'if length > 1 then .[-2].revision else null end')
fi

if [ -z "$REVISION" ] || [ "$REVISION" == "null" ]; then
    echo "No previous revision to roll back to."
    exit 1
fi

echo "Rolling back to revision: $REVISION"

helm rollback $RELEASE_NAME $REVISION --namespace quantacirc-$ENV

echo "Rollback successful."
