"""
vector_search.py

Runs a semantic (vector) search against sample_mflix.movies.
Embeds a user-supplied query with OpenAI, then finds the movies whose
plot_embedding is most similar, using Atlas $vectorSearch.
"""

import os
import sys
from dotenv import load_dotenv
from pymongo import MongoClient
from openai import OpenAI

# --- Configuration ---
EMBEDDING_MODEL = "text-embedding-3-small"
INDEX_NAME = "plot_vector_index"
EMBEDDING_FIELD = "plot_embedding"
NUM_CANDIDATES = 100
NUM_RESULTS = 5

# --- Load secrets ---
load_dotenv()
atlas_uri = os.getenv("ATLAS_URI")
openai_key = os.getenv("OPENAI_API_KEY")

if not atlas_uri or not openai_key:
    print("ERROR: ATLAS_URI or OPENAI_API_KEY not found in .env")
    sys.exit(1)

# --- Connect ---
openai_client = OpenAI(api_key=openai_key)
mongo_client = MongoClient(atlas_uri)
movies = mongo_client["sample_mflix"]["movies"]

# --- Get the search query from the user ---
QUERY_TEXT = input("Enter your search query: ").strip()

if not QUERY_TEXT:
    print("ERROR: search query cannot be empty.")
    sys.exit(1)

# --- Step 1: embed the query text ---
response = openai_client.embeddings.create(
    model=EMBEDDING_MODEL,
    input=QUERY_TEXT,
)
query_vector = response.data[0].embedding

# --- Step 2: run the vector search ---
pipeline = [
    {
        "$vectorSearch": {
            "index": INDEX_NAME,
            "path": EMBEDDING_FIELD,
            "queryVector": query_vector,
            "numCandidates": NUM_CANDIDATES,
            "limit": NUM_RESULTS,
        }
    },
    {
        "$project": {
            "_id": 0,
            "title": 1,
            "year": 1,
            "genres": 1,
            "runtime": 1,
            "cast": 1,
            "imdb.rating": 1,
            "plot": 1,
            "fullplot": 1,
        }
    },
]

results = list(movies.aggregate(pipeline))

# --- Show results ---
print(f"\n{'=' * 70}")
print(f'  Search results for: "{QUERY_TEXT}"')
print(f"{'=' * 70}\n")

if not results:
    print("  No matching movies found.\n")
else:
    for i, movie in enumerate(results, start=1):
        title   = movie.get("title", "Untitled")
        year    = movie.get("year", "—")

        runtime = movie.get("runtime")
        runtime = f"{runtime} min" if runtime else "—"

        genres  = ", ".join(movie.get("genres", [])) or "—"
        rating  = movie.get("imdb", {}).get("rating") or "—"
        cast    = ", ".join(movie.get("cast", [])[:4]) or "—"
        desc    = movie.get("fullplot") or movie.get("plot", "(no description available)")

        print(f"  {i}. {title}  ({year})")
        print(f"     {genres}  |  {runtime}  |  IMDb: {rating}")
        print(f"     Cast: {cast}")
        print(f"     {desc}")
        print(f"  {'-' * 66}\n")

mongo_client.close()