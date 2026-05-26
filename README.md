# atlas-vector-search-ops

A hands-on project that builds semantic search on top of MongoDB Atlas
Vector Search, with the surrounding cloud infrastructure provisioned
as code. The goal was to work through a realistic vector search setup
end to end: infrastructure, data, embeddings, and several kinds of
search query.

The dataset is the MongoDB `sample_mflix` sample database. Movie plots
are turned into embeddings and made searchable by meaning, not just by
keyword.

## What it does

- **Semantic (vector) search** over movie plots. A plain-text query is
  embedded and matched against plot embeddings, so a search for "a
  superhero protecting the city" returns thematically similar movies
  even when they do not contain that exact wording.
- **Filtered vector search**. The semantic search can be narrowed by
  actor, director, genre, and release year, in any combination.
- **Full-text (keyword) search** over movie titles and plots, with
  title matches weighted higher than plot matches.
- **Hybrid search** that combines the semantic and keyword results
  into one ranked list (see the note on hybrid search below).

## Tech stack

- **MongoDB Atlas** (M0 free tier) for the database, vector index, and
  full-text search index
- **OpenAI** `text-embedding-3-small` for generating embeddings
- **Azure** virtual machine as the workstation, provisioned with
  **Terraform**
- **Python** for the embedding and search scripts
- **Git / GitHub** as the source of truth, synced between a laptop and
  the Azure VM

## How it fits together

The Azure VM is the workstation. It connects to MongoDB Atlas (the
database and search engine) and to the OpenAI API (for embeddings).
Terraform provisions the VM and its networking. Code is written on a
laptop, pushed to GitHub, and pulled onto the VM, where the scripts
are run.

```
Laptop  ->  GitHub  ->  Azure VM  ->  MongoDB Atlas
                                  ->  OpenAI API
```

## Repository layout

| Path | Contents |
|------|----------|
| `infra/` | Terraform configuration for the Azure VM and networking |
| `scripts/` | The embedding generation script |
| `queries/` | The search scripts: vector, text, and hybrid |
| `index_definitions/` | JSON definitions for the vector and text search indexes |
| `runbooks/` | Incident write-ups (RCAs) for problems hit during the build |
| `STATUS.md` | Current project status |
| `KNOWN-LIMITATIONS.md` | Honest list of current limitations and scope decisions |

## How it works

**Embeddings.** `scripts/generate_embeddings.py` reads movie plots from
Atlas, sends each to the OpenAI embeddings API, and stores the returned
1536-dimensional vector back on the movie document. A subset of 500
movies is embedded (see `KNOWN-LIMITATIONS.md` for why).

**Vector index.** A vector search index is defined over the embedding
field, plus filter fields for year, genres, cast, and directors. The
definitions are in `index_definitions/`.

**Searching.** The scripts in `queries/` take a plain-text query,
embed it the same way, and run an Atlas aggregation pipeline:

- `vector_search.py` runs semantic search, with optional filters.
- `text_search.py` runs keyword search over title and plot.
- `hybrid_search.py` combines both.

## Setup outline

The project needs a MongoDB Atlas cluster, an OpenAI API key, and an
Azure subscription. In broad terms:

1. Provision the Azure VM with the Terraform config in `infra/`.
2. Create a MongoDB Atlas cluster and load the `sample_mflix` dataset.
3. Put the Atlas connection string and OpenAI API key in a `.env` file
   on the VM (not committed).
4. Install the Python dependencies from `requirements.txt`.
5. Run `scripts/generate_embeddings.py` to generate embeddings.
6. Create the search indexes from `index_definitions/`.
7. Run the search scripts in `queries/`.

Secrets (the `.env` file, Terraform `.tfvars`) are kept out of the
repository.

## A note on hybrid search

Native hybrid search uses the `$rankFusion` aggregation stage, which
requires MongoDB 8.1 or higher when combined with a `$vectorSearch`
sub-pipeline. The M0 free-tier cluster runs MongoDB 8.0.x, and an M0
cluster's version cannot be selected manually. Hybrid search is
therefore validated separately on a paid cluster during the scaling
phase. See `KNOWN-LIMITATIONS.md` for detail.

## Scaling phase

A later phase of this project temporarily upgrades the cluster to a
paid tier to test the setup at a larger scale: embedding the full
dataset, reproducing and diagnosing vector search performance
behaviour, and validating hybrid search on MongoDB 8.1+. That work and
its findings will be documented when complete.

## Incidents

Real problems hit while building this project are written up as RCAs
in `runbooks/`. Each one covers the issue, root cause, troubleshooting
steps, resolution, and prevention.
