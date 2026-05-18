variable "aws_region" {
  description = "AWS region to deploy the minikube host into."
  type        = string
  default     = "eu-central-1"
}

variable "project_name" {
  description = "Name prefix for AWS resources."
  type        = string
  default     = "insiderone-devops"
}

variable "instance_type" {
  description = "EC2 instance type for the minikube host."
  type        = string
  default     = "t3.small"
}

variable "ssh_key_name" {
  description = "Existing AWS EC2 key pair name for SSH access."
  type        = string
}

variable "ssh_allowed_cidr" {
  description = "CIDR allowed to access SSH. Use your public IP with /32."
  type        = string
}

variable "app_node_port" {
  description = "NodePort exposed by the Helm prod values."
  type        = number
  default     = 30080
}
