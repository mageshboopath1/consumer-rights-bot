import json
import os
import sys
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer

def get_embeddings(chunks: List[str]) -> List[List[float]]:
    """
    Takes a list of text chunks and returns a list of their vector embeddings
    using a pre-trained Hugging Face model.

    Args:
        chunks (List[str]): A list of text strings to be embedded.

    Returns:
        List[List[float]]: A list of embedding vectors.
    """
    try:
        # Load the sentence-transformer model.
        # This will download the model the first time it is run.
        model = SentenceTransformer('all-MiniLM-L6-v2')
        print("Model loaded successfully.", file=sys.stderr)
        
        # Generate the embeddings for the chunks
        embeddings = model.encode(chunks, convert_to_tensor=False).tolist()
        
        return embeddings
        
    except Exception as e:
        print(f"An unexpected error occurred during embedding: {e}", file=sys.stderr)
        return []

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Error: Both a chunks JSON file and an output file path must be provided.", file=sys.stderr)
        print("Usage: python embedder.py <path_to_chunks_json> <path_to_output_json>", file=sys.stderr)
        sys.exit(1)
        
    input_json_path: str = sys.argv[1]
    output_json_path: str = sys.argv[2]
    
    if not os.path.exists(input_json_path):
        print(f"Error: The input file at '{input_json_path}' was not found.", file=sys.stderr)
        sys.exit(1)

    try:
        # Read the chunks from the provided JSON file
        with open(input_json_path, 'r') as f:
            chunks: List[str] = json.load(f)

        print(f"Loaded {len(chunks)} chunks from {input_json_path}", file=sys.stderr)
        
        vectors: List[List[float]] = get_embeddings(chunks)

        if vectors:
            with open(output_json_path, 'w') as f:
                json.dump(vectors, f, indent=4)
            print(f"Successfully generated {len(vectors)} embeddings and saved them to '{output_json_path}'.", file=sys.stderr)
            sys.exit(0)
        else:
            print("Embedding failed.", file=sys.stderr)
            sys.exit(1)

    except json.JSONDecodeError:
        print(f"Error: The file at '{input_json_path}' is not a valid JSON file.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)