# Deployment Guide

This guide covers the process of deploying your QuantaCirc project to different environments.

## The `deploy` Command

The primary tool for deployment is the `qc deploy` command. This command packages your project and sends it to the target environment specified in your configuration.

```bash
# Example: Deploying to the staging environment
qc deploy --environment staging
```

## Deployment Configuration

The deployment settings are managed in the `qc_config.yml` file. Here you can define different environments, such as `dev`, `staging`, and `prod`.

```yaml
# qc_config.yml
project_name: MyFirstQCProject

environments:
  staging:
    target: kubernetes
    kube_context: "staging-cluster"
    namespace: "quantacirc-staging"
    replicas: 2

  prod:
    target: kubernetes
    kube_context: "prod-cluster"
    namespace: "quantacirc-prod"
    replicas: 10
    strategy: "blue-green"
```

## Deployment Targets

QuantaCirc supports several deployment targets, providing flexibility for different infrastructure setups.

### 1. Docker

You can build a Docker image of your project directly. The system uses the Dockerfiles located in `/deployment/docker`.

To build an image for your project:
```bash
# This is a hypothetical command, the actual implementation may vary
qc build-image --tag my-project:latest
```

### 2. Kubernetes (with Helm)

For container orchestration, QuantaCirc provides Helm charts to easily deploy your project to a Kubernetes cluster. The charts are located in `/deployment/helm`.

When you run `qc deploy` with a `kubernetes` target, the CLI will use these Helm charts to perform the deployment. You need to have `kubectl` configured with the correct context for this to work.

### 3. Terraform

For managing cloud infrastructure, QuantaCirc provides Terraform modules in `/deployment/terraform`. These modules can be used to provision the necessary resources (e.g., EKS clusters, S3 buckets, RDS databases) on cloud providers like AWS.

Using these Terraform modules is a more advanced topic and is typically done by the infrastructure team. The `qc deploy` command assumes that the underlying infrastructure is already provisioned.

By leveraging these industry-standard tools, QuantaCirc enables you to build a robust and scalable deployment pipeline for your projects.
