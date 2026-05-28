# Provisions a M10 cluster with database user and a network access entry

terraform {
  required_version = ">= 1.5"

  required_providers {
    mongodbatlas = {
      source  = "mongodb/mongodbatlas"
      version = "~> 1.20"
    }
  }
}

# Authenticates with an Atlas Organization API key
provider "mongodbatlas" {
  public_key  = var.atlas_public_key
  private_key = var.atlas_private_key
}

# The M10 dedicated cluster
resource "mongodbatlas_advanced_cluster" "m10" {
  project_id   = var.atlas_project_id
  name         = var.cluster_name
  cluster_type = "REPLICASET"

  mongo_db_major_version = "8.1"

  replication_specs = [
    {
      region_configs = [
        {
          provider_name = "AWS"
          region_name   = "AP_SOUTH_1"
          priority      = 7

          electable_specs = {
            instance_size = "M10"
            node_count    = 3
          }
        }
      ]
    }
  ]
}

# Database user for connecting to the cluster.
resource "mongodbatlas_database_user" "user" {
  project_id         = var.atlas_project_id
  username           = var.db_username
  password           = var.db_password
  auth_database_name = "admin"

  roles {
    role_name     = "atlasAdmin"
    database_name = "admin"
  }
}

# Network access: allow the workstation's public IP to reach the cluster
resource "mongodbatlas_project_ip_access_list" "workstation" {
  project_id = var.atlas_project_id
  ip_address = var.allowed_ip
  comment    = "workstation access"
}