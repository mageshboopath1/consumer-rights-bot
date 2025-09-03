import json
import sys
import os
import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
# Import the shared QueueManager class
from shared.queueManager import QueueManager

# IMPORTANT: Use an HttpClient to connect to a separate ChromaDB service
# The host name 'chromadb-server' should match the service name in your docker-compose.yml file
# The port '8000' is the default for the ChromaDB server
CHROMA_HOST = os.getenv("CHROMA_HOST", "chromadb-server")
CHROMA_PORT = os.getenv("CHROMA_PORT", 8000)

def run_rag_query(user_query: str) -> str:
    """
    Performs a RAG query by:
    1. Embedding the user's query.
    2. Searching a ChromaDB collection for relevant documents.
    3. Constructing a final prompt with the retrieved context.

    Args:
        user_query (str): The PII-filtered query from the user.

    Returns:
        str: A fully-formed prompt containing the context and the user's query.
    """
    try:
        # Step 1: Initialize the ChromaDB client
        client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
        
        # Check if the collection exists before attempting to get it
        collection_name = "document_embeddings"
        try:
            collection = client.get_collection(name=collection_name)
        except Exception:
            print(f"Collection '{collection_name}' not found. Please ensure your documents are ingested.", file=sys.stderr)
            return "No relevant documents found in the knowledge base."

        # Step 2: Load the same embedding model used for ingestion
        model = SentenceTransformer('all-MiniLM-L6-v2')
        query_embedding = model.encode(user_query, convert_to_tensor=False).tolist()

        # Step 3: Perform a semantic search to find the most relevant documents
        search_results = collection.query(
            query_embeddings=[query_embedding],
            n_results=3,
        )

        # Step 4: Extract the retrieved documents
        retrieved_documents = search_results.get('documents', [])
        
        if not retrieved_documents or not retrieved_documents[0]:
            context = "No relevant documents found in the knowledge base."
        else:
            context = " ".join(retrieved_documents[0])

        # Step 5: Construct the final prompt for the LLM
        prompt = (
            "Given the following context, please answer the question. "
            "If the answer is not present in the context, please state that "
            "and do not try to make up an answer.\n\n"
            f"Context:\n{context}\n\n"
            f"Question:\n{user_query}\n"
        )
        
        return prompt

    except Exception as e:
        print(f"An unexpected error occurred in the RAG core: {e}", file=sys.stderr)
        return "" # Return an empty string or handle error gracefully

def rag_core_callback(ch, method, properties, body):
    """
    Callback function to handle incoming messages from the queue.
    It performs the RAG query and publishes the final prompt.
    """
    try:
        # Decode the message body from bytes to a string
        pii_filtered_query = body.decode('utf-8')
        print(f" [x] Received from 'rag_core_queue': {pii_filtered_query}")

        # Run the RAG query with the PII-filtered text
        final_prompt = run_rag_query(pii_filtered_query)
        print(f" [x] Final prompt for LLM: {final_prompt}")
        
        # Publish the final prompt to the next queue in the pipeline (e.g., an LLM queue)
        # Note: You can optionally add a header to identify the message type or sender
        queue_manager.send_message(queue_name='llm_queue', message=final_prompt)

    except Exception as e:
        print(f"Error processing message: {e}", file=sys.stderr)
    
    # Acknowledge the message so it's removed from the queue
    ch.basic_ack(delivery_tag=method.delivery_tag)

if __name__ == "__main__":
    # Initialize the QueueManager
    try:
        queue_manager = QueueManager()
    except Exception as e:
        print(f"Failed to initialize QueueManager: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        # Start listening for messages on the 'rag_core_queue'
        queue_manager.start_listening(queue_name='rag_core_queue', callback=rag_core_callback)
    except KeyboardInterrupt:
        print('Interrupted. Exiting...')
    finally:
        queue_manager.close()