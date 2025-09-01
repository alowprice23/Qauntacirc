# Plan for the `deployment` Directory (v4 - Exhaustive & Comprehensive)

## 1. Guiding Philosophy & Core Principles

The `deployment` directory contains all artifacts necessary to build, containerize, and deploy the QuantaCirc system and the software it generates. The philosophy here is to treat infrastructure and deployment as code, subject to the same rigor as the application itself.

1.  **Infrastructure as Code (IaC)**: All infrastructure is defined declaratively (Terraform), ensuring it is version-controlled, auditable, and reproducible.
2.  **Containerization & Immutability**: All components are containerized (Docker). Images are treated as immutable artifacts. No changes are made to running containers; instead, new images are built and deployed.
3.  **GitOps as the Source of Truth**: The desired state of the system is defined in a Git repository. An automated process (e.g., ArgoCD) ensures that the live environment converges to the state defined in Git.
4.  **Scalability & Resilience**: The deployment architecture is designed for scalability and resilience, with built-in support for horizontal pod autoscaling, high availability, and disaster recovery.
5.  **Multi-Environment Parity**: The deployment scripts and configurations must support multiple environments (local, dev, staging, prod) while maintaining as much parity as possible to prevent environment-specific bugs.

---

## 2. File-by-File Implementation Plan

This plan details every file within the `deployment` directory.

### **Sub-directory: `deployment/docker/`**
*   **Purpose**: Contains all Dockerfiles for building the container images for the system's components.
*   **Key Files**:
    *   **`Dockerfile.base`**: A base image with all the common dependencies, layers, and user setup to speed up subsequent builds.
    *   **`Dockerfile.cli`**: A slim, multi-stage build for the CLI, resulting in a small image for distribution.
    *   **`Dockerfile.agents`**: The main image for running the 10 agent services in a Kubernetes environment.
    *   **`Dockerfile.monitoring`**: An image for the custom monitoring components.
    *   **`build.sh`**: A helper script to build and tag all Docker images according to the version in `version.py`.

### **Sub-directory: `deployment/helm/`**
*   **Purpose**: A Helm chart for managing the Kubernetes deployments in a configurable and reusable way. This is the primary mechanism for deploying QuantaCirc to a Kubernetes cluster.
*   **Key Files**:
    *   **`Chart.yaml`**: The Helm chart metadata.
    *   **`values.yaml`**: The default configuration values for the chart. This file will be extensively documented.
    *   **`templates/`**: A directory containing all the Kubernetes manifest templates, including deployments, services, ingresses, HPAs, and RBAC rules for every component of the system.

### **Sub-directory: `deployment/terraform/`**
*   **Purpose**: Terraform configurations for provisioning the cloud infrastructure needed to run QuantaCirc.
*   **Key Files**:
    *   **`main.tf`, `variables.tf`, `outputs.tf`**: The standard root Terraform files.
    *   **`modules/`**: Reusable modules for creating a VPC, an EKS/GKE/AKS cluster, an S3/GCS bucket for artifacts, and a managed database for the run ledger.
    *   **`environments/`**: Backend configurations for each environment.

### **Sub-directory: `deployment/cicd/`**
*   **Purpose**: CI/CD pipeline definitions for various platforms.
*   **Key Files**:
    *   `.github/workflows/ci.yml`: A comprehensive GitHub Actions workflow for linting, testing, building, and verifying on every push and pull request.
    *   `.github/workflows/cd.yml`: A GitHub Actions workflow for deploying to staging and production, gated by manual approvals and health checks.
    *   ... (and configurations for other CI/CD systems like GitLab and Jenkins).

### **Sub-directory: `deployment/scripts/`**
*   **Purpose**: A collection of utility scripts to automate common deployment and operational tasks.
*   **Key Files**:
    *   `deploy.sh`: A wrapper around `helm upgrade --install` with environment-specific logic.
    *   `rollback.sh`: A script to safely roll back a deployment to a previous version.
    *   `health-check.sh`: A script that checks the health of all deployed components.
