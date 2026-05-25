# Project Status — atlas-vector-search-ops

## Done

Step 1 — Workstation and infrastructure. Azure VM provisioned with Terraform, two-machine Git workflow (laptop + VM) working.
Step 2 — Atlas database. M0 cluster running, sample_mflix loaded, network access and database user configured.
Step 3 — Embeddings. 500 movie plots embedded with OpenAI text-embedding-3-small, stored as 1536-dim vectors.
Step 4 — Vector search. Vector index built; semantic search working, unfiltered and with composable filters (actor, director, genre, year).
Step 5 — Hybrid search. Text search index built; pure text search working. Hybrid search written using $rankFusion — see note below.

## In progress

Step 6 — Documentation. Incident RCAs, known limitations, README, repo cleanup.

## Planned

Step 7 — Scaling phase. Temporary M10 upgrade: load synthetic data at scale, reproduce and diagnose vector-search performance degradation, write RCA. Also validate $rankFusion hybrid search (needs MongoDB 8.1+).

## Note on hybrid search

$rankFusion with a $vectorSearch sub-pipeline requires MongoDB 8.1+. The M0 cluster runs 8.0.x and its version cannot be selected manually. The hybrid search script is written and documented but is validated during the Step 7 M10 phase, where the cluster runs 8.1+.