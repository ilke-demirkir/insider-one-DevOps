output "instance_id" {
  description = "EC2 instance ID."
  value       = aws_instance.minikube.id
}

output "elastic_ip" {
  description = "Elastic IP for the minikube host."
  value       = aws_eip.minikube.public_ip
}

output "ssh_command" {
  description = "SSH command template."
  value       = "ssh ubuntu@${aws_eip.minikube.public_ip}"
}

output "app_url" {
  description = "Expected public app URL after Helm prod deploy."
  value       = "http://${aws_eip.minikube.public_ip}:${var.app_node_port}"
}
