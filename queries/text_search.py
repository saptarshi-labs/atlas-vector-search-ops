"""
text_search.py

Full-text (keyword) search against sample_mflix.movies using Atlas
Search ($search). Matches literal query words in title and plot;
title matches are boosted over plot matches.
"""

import os
import sys
from dotenv import load_dotenv
from pymongo import MongoClient

# --- Configuration ---
TEXT_INDEX = "plot_text_index"
NUM_RESULTS = 5

# --- Load secrets ---
load_dotenv()
atlas_uri = os.getenv("ATLAS_URI")

if not atlas_uri:
    print("ERROR: ATLAS_URI not found in .env")
    sys.exit(1)

# --- Connect ---
mongo_client = MongoClient(atlas_uri)
movies = mongo_client["sample_mflix"]["movies"]

# --- Get the search query from the user ---
QUERY_TEXT = input("Enter your search query: ").strip()

if not QUERY_TEXT:
    print("ERROR: search query cannot be empty.")
    sys.exit(1)

# --- Build the text search pipeline ---
pipeline = [
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
]

results = list(movies.aggregate(pipeline))

# --- Show results ---
print(f"\n{'=' * 70}")
print(f'  Text (keyword) search results for: "{QUERY_TEXT}"')
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