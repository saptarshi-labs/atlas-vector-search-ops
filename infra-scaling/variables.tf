# Input variables for the Atlas infrastructure.

variable "atlas_public_key" {
  description = "Public key of the Atlas API key pair."
  type        = string
}

variable "atlas_private_key" {
  description = "Private key of the Atlas API key pair."
  type        = string
  sensitive   = true
}

variable "atlas_project_id" {
  description = "ID of the existing Atlas project to create resources in."
  type        = string
}

variable "cluster_name" {
  description = "Name for the M10 cluster."
  type        = string
}

variable "db_username" {
  description = "Username for the cluster database user."
  type        = string
}

variable "db_password" {
  description = "Password for the cluster database user."
  type        = string
  sensitive   = true
}

variable "allowed_ip" {
  description = "Public IP allowed to reach the cluster."
  type        = string
}