"""
generate_embeddings.py
Reads movie plots from MongoDB Atlas, generates vector embeddings via the
OpenAI API, and writes each embedding back onto its movie document.
Scope: movies from sample_mflix.movies that have a non-empty plot
and are not yet embedded.
"""

import os
import sys
import time
from dotenv import load_dotenv
from pymongo import MongoClient, UpdateOne
from openai import OpenAI

# --- Configuration ---
EMBEDDING_MODEL = "text-embedding-3-small"
SOURCE_FIELD = "plot"               # field whose text is embedded
EMBEDDING_FIELD = "plot_embedding"  # field where the embedding is stored
PROGRESS_EVERY = 50                 # print a progress line every N movies

DEFAULT_LIMIT = 500                 # movies processed in default mode
SCALED_LIMIT = 20000                # movies processed in scaled mode

BATCH_SIZE = 100                    # plots per OpenAI call in scaled mode

MAX_RETRIES = 3                     # embedding attempts (per movie or per batch)
RETRY_WAIT_SECONDS = 5              # wait between retry attempts

# --- Load secrets from .env ---
load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")

# --- Choose the run mode ---
answer = input("Run in default mode (500 movies, M0 cluster)? [y/n]: ").strip().lower()

if answer == "y":
    mode = "default"
    atlas_uri = os.getenv("ATLAS_URI")
    movie_limit = DEFAULT_LIMIT
    use_retry = False
    use_batching = False
else:
    mode = "scaled"
    atlas_uri = os.getenv("ATLAS_URI_M10")
    movie_limit = SCALED_LIMIT
    use_retry = True
    use_batching = True

print(f"Mode: {mode}. Movie limit: {movie_limit}. Batching: {use_batching}.")

if not atlas_uri:
    print(f"ERROR: connection string not found in .env for {mode} mode")
    sys.exit(1)

if not openai_key:
    print("ERROR: OPENAI_API_KEY not found in .env")
    sys.exit(1)

# --- Connect to OpenAI and MongoDB ---
openai_client = OpenAI(api_key=openai_key)
mongo_client = MongoClient(atlas_uri)
movies = mongo_client["sample_mflix"]["movies"]

# --- Select movies that have the source field and are not yet embedded ---
query = {
    SOURCE_FIELD: {"$exists": True, "$ne": ""},
    EMBEDDING_FIELD: {"$exists": False},
}
# Fetch only the fields used: _id (to update), title (logging), source field (to embed)
projection = {"_id": 1, "title": 1, SOURCE_FIELD: 1}
cursor = movies.find(query, projection).limit(movie_limit)


# --- Helper: call the OpenAI API, with optional retry ---
def embed_texts(texts):
    attempts = MAX_RETRIES if use_retry else 1
    for attempt in range(1, attempts + 1):
        try:
            response = openai_client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=texts,
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            if attempt < attempts:
                print(f"  attempt {attempt} failed ({e}); retrying in {RETRY_WAIT_SECONDS}s")
                time.sleep(RETRY_WAIT_SECONDS)
            else:
                raise


# --- Process each movie ---
processed = 0
failed_movies = []


# --- Helper: embed and store one batch of movies ---
def process_batch(batch):
    global processed

    texts = [m[SOURCE_FIELD] for m in batch]

    # --- embed the whole batch in one API call ---
    try:
        embeddings = embed_texts(texts)
    except Exception as e:
        for m in batch:
            failed_movies.append((m.get("title", "<untitled>"), str(e)))
        print(f"FAILED to embed batch of {len(batch)} -- {e}")
        return

    operations = []
    for movie, embedding in zip(batch, embeddings):
        operations.append(
            UpdateOne(
                {"_id": movie["_id"]},
                {"$set": {EMBEDDING_FIELD: embedding}},
            )
        )

    try:
        movies.bulk_write(operations)
        processed += len(operations)
        print(f"[{processed}] embedded so far...")
    except Exception as e:
        for m in batch:
            failed_movies.append((m.get("title", "<untitled>"), str(e)))
        print(f"FAILED to write batch of {len(batch)} -- {e}")


# --- Process the movies ---
if use_batching:
    batch = []
    for movie in cursor:
        batch.append(movie)
        if len(batch) == BATCH_SIZE:
            process_batch(batch)
            batch = []
    if batch:
        process_batch(batch)
else:
    for movie in cursor:
        title = movie.get("title", "<untitled>")
        text = movie[SOURCE_FIELD]
        try:
            embeddings = embed_texts([text])
            movies.update_one(
                {"_id": movie["_id"]},
                {"$set": {EMBEDDING_FIELD: embeddings[0]}},
            )
            processed += 1
            if processed % PROGRESS_EVERY == 0:
                print(f"[{processed}] embedded so far...")
        except Exception as e:
            failed_movies.append((title, str(e)))
            print(f"FAILED: {title} -- {e}")

# --- Summary ---
print(f"\nDone. Mode: {mode}. Embedded: {processed}, Failed: {len(failed_movies)}")

if failed_movies:
    print("\n--- Failed movies ---")
    for title, error in failed_movies:
        print(f"  {title} -- {error}")

mongo_client.close()