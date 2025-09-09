variable "aws_region" {
  description = "The AWS region to deploy the infrastructure in."
  type        = string
  default     = "us-west-2"
}

variable "project_name" {
  description = "The name of the project."
  type        = string
  default     = "quantacirc"
}

variable "cluster_name" {
  description = "The name of the Kubernetes cluster."
  type        = string
  default     = "quantacirc-cluster"
}

variable "vpc_cidr" {
  description = "The CIDR block for the VPC."
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "A list of CIDR blocks for the public subnets."
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "A list of CIDR blocks for the private subnets."
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24"]
}

variable "node_group_instance_type" {
  description = "The instance type for the EKS worker nodes."
  type        = string
  default     = "t3.medium"
}

variable "db_name" {
  description = "The name of the database."
  type        = string
  default     = "quantacircdb"
}

variable "db_username" {
  description = "The username for the database."
  type        = string
  default     = "quantacirc"
}

variable "db_password" {
  description = "The password for the database."
  type        = string
  sensitive   = true
}

variable "s3_bucket_name" {
  description = "The name of the S3 bucket for artifacts. Must be globally unique."
  type        = string
  default     = "quantacirc-artifacts-unique-placeholder"
}
