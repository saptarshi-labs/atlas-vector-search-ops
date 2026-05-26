# Known Limitations

Honest list of the current limitations of this project. Some are
deliberate scope decisions, some are gaps that would need work before
this could be considered production ready. A separate scaling phase
(running the project on a larger, paid cluster) is planned, and some
of the limitations below will be revisited then.

## 1. The Atlas cluster is not provisioned as code

The Azure VM is provisioned as code with Terraform, but the MongoDB
Atlas cluster was created manually through the Atlas web console. In a
production setup the cluster would also be provisioned as code, for
consistency and reproducibility, for example with the MongoDB Atlas
Terraform provider, which can manage the cluster, database users,
network access rules, and search indexes alongside the existing Azure
infrastructure.

The temporary tier upgrade in the scaling phase is likewise done
manually (through the Atlas console or the Atlas CLI) rather than
through Terraform. That is a deliberate choice: it is a supervised,
temporary, reversible tier change rather than standing infrastructure,
so the overhead of importing the hand-created cluster into Terraform
state was not worth it. The production-correct approach for a dedicated
cluster is a clean create-and-destroy managed by the Atlas Terraform
provider.

## 2. Duplicate documents in the sample data

The `sample_mflix.movies` collection contains duplicate movie records,
where the same film appears as two separate documents. Both copies get
embedded, so a vector search can return the same movie twice (this was
seen with the film "Torment"). This is a data quality issue in the
source dataset, not a search bug. The search is correctly returning
two documents that happen to describe the same film. Deduplicating
during data ingestion, or with a grouping stage in the query, would
fix it.

## 3. Embedding script hardening gaps

`generate_embeddings.py` is written for a one-off run of 500 documents
and is not hardened for production use. Specifically:

- No retry or backoff for transient OpenAI API failures. A failed call
  is logged and skipped, not retried.
- No batching. Each plot is sent as its own API call. The OpenAI
  embeddings API accepts multiple inputs per request, which would be
  far more efficient at scale.
- No checkpoint or resume. A crash midway means re-running, and while
  the query skips already-embedded documents, there is no proper
  resumable state.
- Uses `print` for output rather than structured logging.

For the 500-document scope this is fine. At larger scale, retry,
batching, and resumability would be needed.

## 4. Hybrid search requires MongoDB 8.1+

Native hybrid search uses the `$rankFusion` aggregation stage. When
`$rankFusion` includes a `$vectorSearch` sub-pipeline, it requires
MongoDB 8.1 or higher. The M0 free-tier cluster used for the core
project runs MongoDB 8.0.x, and the MongoDB version of an M0 cluster
cannot be selected manually (M0 is auto-managed by Atlas).

On 8.0.x the hybrid search script runs without an error but does not
genuinely fuse the two pipelines, so hybrid results collapse to the
vector results alone. The hybrid search script is therefore validated
later, during the scaling phase on a paid cluster running 8.1+. A
version-independent alternative is manual Reciprocal Rank Fusion built
from standard aggregation stages.

## 5. Filtering is exact match only

The filters in the vector search (actor, director, genre) use exact,
case-sensitive matching. A misspelled or partial name returns no
results. For example, "tom hanks" in lower case will not match a
document stored as "Tom Hanks". Fuzzy or partial name matching would
require full-text search rather than the filter clause of
`$vectorSearch`.

## 6. Only a 500-document subset is embedded

Of the roughly 21,000 movies in `sample_mflix.movies`, only 500 are
embedded. This is a deliberate decision: the embeddings plus the vector
index would exceed the 512 MB storage limit of the M0 free tier if all
documents were embedded. The trade-off is that search quality and
result variety are bounded by this subset, and a search may miss a
genuinely relevant movie simply because it was not among the embedded
500. Full-scale embedding is planned as part of the later scaling phase
on a larger cluster.
