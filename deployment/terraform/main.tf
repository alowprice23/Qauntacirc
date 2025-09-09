# Main Terraform configuration for QuantaCirc infrastructure

provider "aws" {
  region = var.aws_region
}

data "aws_availability_zones" "available" {}

module "vpc" {
  source = "./modules/vpc"

  project_name          = var.project_name
  vpc_cidr              = var.vpc_cidr
  availability_zones    = data.aws_availability_zones.available.names
  public_subnet_cidrs   = var.public_subnet_cidrs
  private_subnet_cidrs  = var.private_subnet_cidrs
}

module "eks" {
  source = "./modules/eks"

  cluster_name    = var.cluster_name
  subnet_ids      = module.vpc.private_subnet_ids
  node_group_instance_type = var.node_group_instance_type
}

module "rds" {
  source = "./modules/rds"

  project_name          = var.project_name
  vpc_id                = module.vpc.vpc_id
  private_subnet_ids    = module.vpc.private_subnet_ids
  # This requires the EKS cluster to have a security group.
  # The aws_eks_cluster resource creates one by default.
  eks_cluster_security_group_id = module.eks.cluster_security_group_id
  db_name               = var.db_name
  db_username           = var.db_username
  db_password           = var.db_password
}

module "s3" {
  source = "./modules/s3"

  project_name = var.project_name
  bucket_name  = var.s3_bucket_name
}
