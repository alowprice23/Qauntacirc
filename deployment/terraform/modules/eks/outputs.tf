output "cluster_name" {
  description = "The name of the EKS cluster."
  value       = aws_eks_cluster.main.name
}

output "cluster_endpoint" {
  description = "The endpoint for the EKS cluster."
  value       = aws_eks_cluster.main.endpoint
}

output "cluster_ca_certificate" {
  description = "The CA certificate for the EKS cluster."
  value       = aws_eks_cluster.main.certificate_authority[0].data
}

output "cluster_oidc_provider" {
  description = "The OIDC provider for the EKS cluster."
  value       = aws_eks_cluster.main.identity[0].oidc[0].issuer
}

output "cluster_security_group_id" {
  description = "The security group ID of the EKS cluster."
  value       = aws_eks_cluster.main.vpc_config[0].cluster_security_group_id
}
