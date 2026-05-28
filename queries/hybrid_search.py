"""
hybrid_search.py

Hybrid search against sample_mflix.movies: combines semantic vector
search ($vectorSearch on plot_embedding) with full-text keyword search
($search on title and plot), fused with the native $rankFusion stage.
Title matches are boosted over plot matches in the text pipeline.
"""

import os
import sys
from dotenv import load_dotenv
from pymongo import MongoClient
from openai import OpenAI

# --- Configuration ---
EMBEDDING_MODEL = "text-embedding-3-small"
VECTOR_INDEX = "plot_vector_index"
TEXT_INDEX = "plot_text_index"
EMBEDDING_FIELD = "plot_embedding"
NUM_CANDIDATES = 100
NUM_RESULTS = 5

# weights for combining the two search methods in $rankFusion
VECTOR_WEIGHT = 0.6
TEXT_WEIGHT = 0.4

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

# --- Embed the query text (for the vector pipeline) ---
response = openai_client.embeddings.create(
    model=EMBEDDING_MODEL,
    input=QUERY_TEXT,
)
query_vector = response.data[0].embedding

# --- Build the hybrid pipeline ---
pipeline = [
    {
        "$rankFusion": {
            "input": {
                "pipelines": {
                    # Pipeline 1: semantic vector search
                    "vectorPipeline": [
                        {
                            "$vectorSearch": {
                                "index": VECTOR_INDEX,
                                "path": EMBEDDING_FIELD,
                                "queryVector": query_vector,
                                "numCandidates": NUM_CANDIDATES,
                                "limit": NUM_RESULTS,
                            }
                        }
                    ],
                    # Pipeline 2: full-text keyword search (title boosted)
                    "textPipeline": [
                        {
                            "$search": {
                                "index": TEXT_INDEX,
                                "compound": {
                                    "should": [
                                        {
                                            "text": {
                                                "query": QUERY_TEXT,
                                                "path": "title",
                                                "score": {"boost": {"value": 3}},
                                            }
                                        },
                                        {
                                            "text": {
                                                "query": QUERY_TEXT,
                                                "path": "plot",
                                            }
                                        },
                                    ]
                                },
                            }
                        },
                        {"$limit": NUM_RESULTS},
                    ],
                }
            },
            "combination": {
                "weights": {
                    "vectorPipeline": VECTOR_WEIGHT,
                    "textPipeline": TEXT_WEIGHT,
                }
            },
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
            "directors": 1,
            "imdb.rating": 1,
            "plot": 1,
            "fullplot": 1,
        }
    },
    {"$limit": NUM_RESULTS},
]

results = list(movies.aggregate(pipeline))

# --- Show results ---
print(f"\n{'=' * 70}")
print(f'  Hybrid search results for: "{QUERY_TEXT}"')
print(f"  (vector weight {VECTOR_WEIGHT}, text weight {TEXT_WEIGHT})")
print(f"{'=' * 70}\n")

if not results:
    print("  No matching movies found.\n")
else:
    for i, movie in enumerate(results, start=1):
        title    = movie.get("title", "Untitled")
        year     = movie.get("year", "—")

        runtime  = movie.get("runtime")
        runtime  = f"{runtime} min" if runtime else "—"

        genres   = ", ".join(movie.get("genres", [])) or "—"
        rating   = movie.get("imdb", {}).get("rating") or "—"
        cast     = ", ".join(movie.get("cast", [])[:4]) or "—"
        director = ", ".join(movie.get("directors", [])) or "—"
        desc     = movie.get("fullplot") or movie.get("plot", "(no description available)")

        print(f"  {i}. {title}  ({year})")
        print(f"     {genres}  |  {runtime}  |  IMDb: {rating}")
        print(f"     Director: {director}")
        print(f"     Cast: {cast}")
        print(f"     {desc}")
        print(f"  {'-' * 66}\n")

mongo_client.close()