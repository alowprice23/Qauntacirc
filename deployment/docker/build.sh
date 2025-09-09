#!/bin/bash
set -eo pipefail

# --- Configuration ---
# Default registry, can be overridden by environment variable
DOCKER_REGISTRY=${DOCKER_REGISTRY:-"quantacirc"}
VERSION_FILE="version.py"

# --- Argument Parsing ---
PUSH_IMAGES=false
SCAN_IMAGES=false

for arg in "$@"; do
  case $arg in
    --push)
      PUSH_IMAGES=true
      shift
      ;;
    --scan)
      SCAN_IMAGES=true
      shift
      ;;
    *)
      ;;
  esac
done

# --- Helper Functions ---
info() {
  echo "[INFO] $1"
}

warn() {
  echo "[WARN] $1"
}

error() {
  echo "[ERROR] $1" >&2
  exit 1
}

# --- Pre-flight Checks ---
if ! command -v docker &> /dev/null; then
  error "Docker is not installed. Please install Docker to continue."
fi

if ! docker info &> /dev/null; then
  error "Docker daemon is not running. Please start Docker to continue."
fi

if [ "$SCAN_IMAGES" = true ] && ! command -v trivy &> /dev/null; then
  warn "Trivy is not installed, but --scan flag was provided. Skipping vulnerability scan."
  SCAN_IMAGES=false
fi

# --- Main Script ---
info "Starting QuantaCirc Docker image build process..."

# Get the version from the root version.py file
if [ ! -f "../../$VERSION_FILE" ]; then
    error "Version file not found at ../../$VERSION_FILE. This script should be run from the deployment/docker directory."
fi
VERSION=$(python -c "import sys; sys.path.append('../..'); from version import VERSION; print(VERSION)")
info "Building images for version: $VERSION"

# Define images to build
declare -A images
images=(
  ["base"]="Dockerfile.base"
  ["cli"]="Dockerfile.cli"
  ["agents"]="Dockerfile.agents"
  ["monitoring"]="Dockerfile.monitoring"
)

# Build, scan, and push images
for name in "${!images[@]}"; do
  dockerfile="${images[$name]}"
  image_name="quantacirc-$name"
  full_tag="$DOCKER_REGISTRY/$image_name:$VERSION"
  latest_tag="$DOCKER_REGISTRY/$image_name:latest"

  info "Building $image_name from $dockerfile..."
  docker build -f "$dockerfile" -t "$full_tag" ../../
  docker tag "$full_tag" "$latest_tag"
  info "Successfully built and tagged $full_tag and $latest_tag"

  if [ "$SCAN_IMAGES" = true ]; then
    info "Scanning $full_tag for vulnerabilities..."
    trivy image --exit-code 0 --severity HIGH,CRITICAL "$full_tag"
    info "Vulnerability scan for $full_tag completed."
  fi

  if [ "$PUSH_IMAGES" = true ]; then
    info "Pushing $full_tag to registry..."
    docker push "$full_tag"
    info "Pushing $latest_tag to registry..."
    docker push "$latest_tag"
    info "Successfully pushed $image_name to $DOCKER_REGISTRY"
  fi
done

info "Docker image build process completed successfully."
