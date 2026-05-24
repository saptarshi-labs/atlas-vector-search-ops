"""
generate_embeddings.py
Reads movie plots from MongoDB Atlas, generates vector embeddings via the
OpenAI API, and writes each embedding back onto its movie document.
Scope: 500 movies from sample_mflix.movies that have a non-empty plot
and are not yet embedded.
"""

import os
import sys
from dotenv import load_dotenv
from pymongo import MongoClient
from openai import OpenAI

# --- Configuration ---
MOVIE_LIMIT = 500
EMBEDDING_MODEL = "text-embedding-3-small"
SOURCE_FIELD = "plot"               # field whose text is embedded
EMBEDDING_FIELD = "plot_embedding"  # field where the embedding is stored
PROGRESS_EVERY = 50                 # print a progress line every N movies

# --- Load secrets from .env ---
load_dotenv()
atlas_uri = os.getenv("ATLAS_URI")
openai_key = os.getenv("OPENAI_API_KEY")

if not atlas_uri or not openai_key:
    print("ERROR: ATLAS_URI or OPENAI_API_KEY not found in .env")
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
cursor = movies.find(query, projection).limit(MOVIE_LIMIT)

# --- Process each movie ---
processed = 0
failed_movies = []   # collects (title, error) tuples for the end-of-run summary

for movie in cursor:
    title = movie.get("title", "<untitled>")
    text = movie[SOURCE_FIELD]

    try:
        response = openai_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text,
        )
        embedding = response.data[0].embedding

        movies.update_one(
            {"_id": movie["_id"]},
            {"$set": {EMBEDDING_FIELD: embedding}},
        )

        processed += 1
        if processed % PROGRESS_EVERY == 0:
            print(f"[{processed}] embedded so far...")

    except Exception as e:
        failed_movies.append((title, str(e)))
        print(f"FAILED: {title} -- {e}")

# --- Summary ---
print(f"\nDone. Embedded: {processed}, Failed: {len(failed_movies)}")

if failed_movies:
    print("\n--- Failed movies ---")
    for title, error in failed_movies:
        print(f"  {title} -- {error}")

mongo_client.close()