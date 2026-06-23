# build_pinecone_index.py
import os
import time
from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer

# Load credentials securely from the local .env mapping
load_dotenv()

def upload_to_cloud_vector_space():
    api_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX_NAME")
    
    if not api_key or not index_name:
        print("Error: Missing configuration keys in your .env file.")
        return

    # 1. Initialize regional cloud clients and embedding model
    print("Connecting to Pinecone Cloud Service...")
    pc = Pinecone(api_key=api_key)
    index = pc.Index(index_name)
    
    print("Initializing Local Text Vectorization Model...")
    encoder = SentenceTransformer('all-MiniLM-L6-v2')
    
    document_path = "data/document_map.txt"
    if not os.path.exists(document_path):
        print(f"Error: {document_path} not found. Run generate_mock_data.py first.")
        return

    print(f"Parsing raw administrative logs from {document_path}...")
    with open(document_path, "r") as f:
        documents = [line.strip() for line in f.readlines() if line.strip()]
        
    total_logs = len(documents)
    print(f"Found {total_logs} items. Commencing optimized network batch upload...")

    # 2. Process and upload logs in chunks to stay well within network limits
    BATCH_SIZE = 200
    for i in range(0, total_logs, BATCH_SIZE):
        batch_docs = documents[i:i + BATCH_SIZE]
        
        # Vectorize text into memory matrices
        embeddings = encoder.encode(batch_docs)
        
        # Structure the payload data points for Pinecone ingestion
        upsert_payload = []
        for j, text in enumerate(batch_docs):
            global_idx = i + j
            vector_id = f"log_{global_idx:05d}"
            
            # Pinecone lets us save the raw text log straight inside the 'metadata' object
            # so we can easily read it back later without needing a separate database lookup
            upsert_payload.append((
                vector_id, 
                embeddings[j].tolist(), 
                {"text_log": text}
            ))
            
        # Send payload batch securely via API connection
        index.upsert(vectors=upsert_payload)
        print(f"Successfully streamed and indexed elements {i} to {i + len(batch_docs)}...")
        time.sleep(0.1) # Small rest window to avoid network rate limits

    print("\nSuccess! Your cloud vector index is fully populated and ready for operational searches.")

if __name__ == "__main__":
    upload_to_cloud_vector_space()