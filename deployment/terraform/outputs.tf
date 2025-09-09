# Terraform output definitions for QuantaCirc infrastructure

output "vpc_id" {
  description = "The ID of the VPC."
  value       = aws_vpc.main.id
}

output "cluster_endpoint" {
  description = "The endpoint for the Kubernetes cluster."
  value       = aws_eks_cluster.main.endpoint
}

output "cluster_ca_certificate" {
  description = "The CA certificate for the Kubernetes cluster."
  value       = base64decode(aws_eks_cluster.main.certificate_authority[0].data)
  sensitive   = true
}
