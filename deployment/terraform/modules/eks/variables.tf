variable "cluster_name" {
  description = "The name of the EKS cluster."
  type        = string
}

variable "subnet_ids" {
  description = "A list of subnet IDs for the EKS cluster and node group."
  type        = list(string)
}

variable "node_group_desired_size" {
  description = "The desired number of worker nodes."
  type        = number
  default     = 2
}

variable "node_group_max_size" {
  description = "The maximum number of worker nodes."
  type        = number
  default     = 3
}

variable "node_group_min_size" {
  description = "The minimum number of worker nodes."
  type        = number
  default     = 1
}

variable "node_group_instance_type" {
  description = "The instance type for the worker nodes."
  type        = string
  default     = "t3.medium"
}
