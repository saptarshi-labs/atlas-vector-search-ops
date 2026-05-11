# atlas-vector-search-ops

Hands-on project: MongoDB Atlas Vector Search on a Terraform-provisioned Azure VM.

## Stack

- **Azure VM** (Ubuntu 22.04, Standard_B1s, free tier) — workstation
- **MongoDB Atlas** (M0 free tier, AWS Mumbai) — database + vector search
- **OpenAI API** (text-embedding-3-small) — embedding generation
- **Terraform** — infrastructure as code
- **GitHub** — source of truth, syncs laptop and VM

## Repo structure

- `infra/` — Terraform configuration for the Azure VM
- `scripts/` — Python script to generate embeddings
- `index_definitions/` — JSON definitions for vector and text indexes
- `queries/` — mongosh scripts for vector / filtered / hybrid search
- `runbooks/` — operational documentation

## Status

Work in progress. Following a phased build:
- Step 1: Workstation and infrastructure
- Step 2: Atlas cluster and sample data
- Step 3: Embedding generation
- Step 4: Vector index and querying
- Step 5: Hybrid search and performance
- Step 6: Documentation