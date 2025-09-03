import json
import os
import sys
from typing import List, Dict, Any
import chromadb

def ingest_data(chunks_path: str, embeddings_path: str):
    """
    Reads chunks and embeddings from JSON files and writes them to a ChromaDB collection.

    Args:
        chunks_path (str): The path to the JSON file containing text chunks.
        embeddings_path (str): The path to the JSON file containing embedding vectors.
    """
    try:
        # Load chunks from the JSON file
        with open(chunks_path, 'r') as f:
            chunks: List[str] = json.load(f)

        # Load embeddings from the JSON file
        with open(embeddings_path, 'r') as f:
            embeddings: List[List[float]] = json.load(f)

        if len(chunks) != len(embeddings):
            print("Error: The number of chunks and embeddings do not match.", file=sys.stderr)
            sys.exit(1)

        print(f"Loaded {len(chunks)} chunks and embeddings. Preparing to ingest into ChromaDB.", file=sys.stderr)

        # Use a persistent client to ensure the data is saved to disk.
        # This needs to be the same path as your collection lister script.
        client = chromadb.PersistentClient(path="./chroma_data")

        # We'll create a collection to store our document data.
        # The Sentence-Transformers model has an output dimension of 384.
        try:
            collection = client.create_collection(
                name="document_embeddings",
                embedding_function=None, # We're providing pre-computed embeddings
                metadata={"dimension": 384}
            )
            print("Successfully created a new ChromaDB collection: 'document_embeddings'", file=sys.stderr)
        except Exception:
            # If the collection already exists, we can get it.
            collection = client.get_collection(name="document_embeddings")
            print("Connected to existing ChromaDB collection: 'document_embeddings'", file=sys.stderr)

        # Generate unique IDs for each document based on a simple counter
        ids = [f"doc_{i}" for i in range(len(chunks))]
        
        # Add the documents to the collection
        collection.add(
            embeddings=embeddings,
            documents=chunks,
            ids=ids
        )
        print("Successfully ingested all documents into ChromaDB.", file=sys.stderr)

    except json.JSONDecodeError:
        print("Error: One of the input files is not a valid JSON file.", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("Error: One or more input files were not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred during ingestion: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Error: Both a chunks JSON file and an embeddings JSON file must be provided.", file=sys.stderr)
        print("Usage: python vector_db_writer.py <path_to_chunks_json> <path_to_embeddings_json>", file=sys.stderr)
        sys.exit(1)

    chunks_file = sys.argv[1]
    embeddings_file = sys.argv[2]
    
    ingest_data(chunks_file, embeddings_file)