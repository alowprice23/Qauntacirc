output "db_instance_address" {
  description = "The address of the database instance."
  value       = aws_db_instance.main.address
}

output "db_instance_port" {
  description = "The port of the database instance."
  value       = aws_db_instance.main.port
}

output "db_instance_name" {
  description = "The name of the database."
  value       = aws_db_instance.main.db_name
}
