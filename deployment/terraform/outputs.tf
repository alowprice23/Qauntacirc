output "cluster_name" {
  description = "The name of the EKS cluster."
  value       = module.eks.cluster_name
}

output "cluster_endpoint" {
  description = "The endpoint for the EKS cluster."
  value       = module.eks.cluster_endpoint
}

output "cluster_ca_certificate" {
  description = "The CA certificate for the EKS cluster."
  value       = module.eks.cluster_ca_certificate
}

output "db_instance_address" {
  description = "The address of the database instance."
  value       = module.rds.db_instance_address
}

output "s3_bucket_name" {
  description = "The name of the S3 bucket."
  value       = module.s3.bucket_name
}
