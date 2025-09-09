#!/bin/bash
set -e

# Get the version from the root version.py file
VERSION=$(python -c "import sys; sys.path.append('.'); from version import VERSION; print(VERSION)")

echo "Building QuantaCirc Docker images for version: $VERSION"

# Build the base image first
docker build -f Dockerfile.base -t quantacirc/quantacirc-base:$VERSION .
docker tag quantacirc/quantacirc-base:$VERSION quantacirc/quantacirc-base:latest

# Build the CLI image
docker build -f Dockerfile.cli -t quantacirc/quantacirc-cli:$VERSION .
docker tag quantacirc/quantacirc-cli:$VERSION quantacirc/quantacirc-cli:latest

# Build the agents image
docker build -f Dockerfile.agents -t quantacirc/quantacirc-agents:$VERSION .
docker tag quantacirc/quantacirc-agents:$VERSION quantacirc/quantacirc-agents:latest

# Build the monitoring image
docker build -f Dockerfile.monitoring -t quantacirc/quantacirc-monitoring:$VERSION .
docker tag quantacirc/quantacirc-monitoring:$VERSION quantacirc/quantacirc-monitoring:latest

echo "All images built and tagged successfully."
