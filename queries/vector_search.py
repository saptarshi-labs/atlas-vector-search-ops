"""
vector_search.py

Runs a semantic (vector) search against sample_mflix.movies.
Embeds a user-supplied query with OpenAI, then finds the movies whose
plot_embedding is most similar, using Atlas $vectorSearch.
Search is based on the plot embedding; results display fullplot when
available, falling back to the short plot otherwise.
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
            "plot": 1,
            "fullplot": 1,
            "score": {"$meta": "vectorSearchScore"},
        }
    },
]

results = movies.aggregate(pipeline)

# --- Show results ---
print(f"\nQuery: \"{QUERY_TEXT}\"\n")
for i, movie in enumerate(results, start=1):
    description = movie.get("fullplot") or movie.get("plot", "(no plot available)")
    print(f"{i}. {movie['title']}  (score: {movie['score']:.4f})")
    print(f"   {description}\n")

mongo_client.close()