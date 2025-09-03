import sys
import chromadb

def list_all_collections():
    """
    Connects to a persistent ChromaDB instance and lists all available collections.
    """
    try:
        # Use a persistent ChromaDB client by specifying a path.
        # This ensures you connect to the same database on disk.
        client = chromadb.PersistentClient(path="./chroma_data")
        
        # Get the list of collections
        collections = client.list_collections()
        
        if not collections:
            print("No collections found in the database.")
            return

        print("Available ChromaDB Collections:")
        print("-" * 30)
        
        # Iterate through the collections and print their names
        for collection in collections:
            # The collection object has a 'name' property
            print(f"- {collection.name}")

    except Exception as e:
        print(f"An error occurred while listing collections: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    list_all_collections()