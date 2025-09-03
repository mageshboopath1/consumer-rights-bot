import fitz  # PyMuPDF library
import re
import sys
import os
import json
from typing import List

def chunk_document(file_path: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Reads a PDF file, extracts the text, and splits it into chunks.

    Args:
        file_path (str): The path to the PDF document.
        chunk_size (int): The maximum number of characters per chunk.
        overlap (int): The number of characters to overlap between chunks to maintain context.

    Returns:
        List[str]: A list of text chunks.
    """
    if not os.path.exists(file_path):
        # We print to stderr so the JSON output is not polluted
        print(f"Error: The file at '{file_path}' was not found.", file=sys.stderr)
        return []

    try:
        # Open the PDF document
        doc = fitz.open(file_path)
        full_text = ""
        for page in doc:
            full_text += page.get_text()

        # Clean up the text by replacing multiple newlines and spaces
        full_text = re.sub(r'\s+', ' ', full_text).strip()

        # A simple fixed-size chunking strategy
        chunks = []
        if len(full_text) <= chunk_size:
            return [full_text]

        start = 0
        while start < len(full_text):
            end = start + chunk_size
            chunks.append(full_text[start:end])
            start += chunk_size - overlap

        return chunks
    except Exception as e:
        print(f"An unexpected error occurred during chunking: {e}", file=sys.stderr)
        return []

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Error: Both a PDF file path and an output file path must be provided.", file=sys.stderr)
        print("Usage: python chunker.py <path_to_pdf> <path_to_output_json>", file=sys.stderr)
        sys.exit(1)

    pdf_path = sys.argv[1]
    output_path = sys.argv[2]
    
    # Chunk the document from the provided path
    chunks_list = chunk_document(pdf_path, chunk_size=500, overlap=50)

    if chunks_list:
        try:
            with open(output_path, 'w') as f:
                json.dump(chunks_list, f, indent=4)
            print(f"Successfully created {len(chunks_list)} chunks and wrote them to '{output_path}'.", file=sys.stderr)
            sys.exit(0)
        except IOError as e:
            print(f"Error writing to file '{output_path}': {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("Chunking failed. No output generated.", file=sys.stderr)
        sys.exit(1)
