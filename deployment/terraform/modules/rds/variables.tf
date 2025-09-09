variable "project_name" {
  description = "The name of the project."
  type        = string
}

variable "vpc_id" {
  description = "The ID of the VPC."
  type        = string
}

variable "private_subnet_ids" {
  description = "A list of private subnet IDs for the database."
  type        = list(string)
}

variable "eks_cluster_security_group_id" {
  description = "The security group ID of the EKS cluster to allow traffic from."
  type        = string
}

variable "db_allocated_storage" {
  description = "The allocated storage for the database."
  type        = number
  default     = 20
}

variable "db_instance_class" {
  description = "The instance class for the database."
  type        = string
  default     = "db.t3.micro"
}

variable "db_name" {
  description = "The name of the database."
  type        = string
}

variable "db_username" {
  description = "The username for the database."
  type        = string
}

variable "db_password" {
  description = "The password for the database."
  type        = string
  sensitive   = true
}
