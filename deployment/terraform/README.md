# Terraform Infrastructure for QuantaCirc

This directory contains the Terraform configuration for provisioning the cloud infrastructure required to run the QuantaCirc system.

## Usage

1.  **Initialize Terraform:**
    ```bash
    terraform init
    ```

2.  **Plan the deployment:**
    ```bash
    terraform plan
    ```

3.  **Apply the changes:**
    ```bash
    terraform apply
    ```

## Multi-Environment Support

This Terraform configuration supports multiple environments (e.g., dev, staging, prod) through the use of workspace or separate state files. Environment-specific variables can be provided using `.tfvars` files.
