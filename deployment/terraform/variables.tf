# Terraform variable definitions for QuantaCirc infrastructure

variable "aws_region" {
  description = "The AWS region to deploy the infrastructure in."
  type        = string
  default     = "us-west-2"
}

variable "cluster_name" {
  description = "The name of the Kubernetes cluster."
  type        = string
  default     = "quantacirc-cluster"
}

variable "db_password" {
  description = "The password for the database."
  type        = string
  sensitive   = true
}
