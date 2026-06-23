# build_vector_index.py
import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

def generate_production_vector_space():
    print("Initializing SentenceTransformer model ('all-MiniLM-L6-v2')...")
    encoder = SentenceTransformer('all-MiniLM-L6-v2')
    
    document_path = "data/document_map.txt"
    index_output_path = "data/knowledge_layer.index"
    
    if not os.path.exists(document_path):
        print(f"Error: {document_path} not found. Run generate_mock_data.py first.")
        return

    print(f"Reading generated operational logs from {document_path}...")
    with open(document_path, "r") as f:
        documents = [line.strip() for line in f.readlines() if line.strip()]
        
    total_docs = len(documents)
    print(f"Loaded {total_docs} total logs. Commencing vector embedding calculation...")
    
    # Encode all documents into high-dimensional vector space (384 dimensions)
    # Using batch processing to ensure stability under larger datasets
    print("⚡ Vectorizing text matrix (this may take a few moments)...")
    embeddings = encoder.encode(documents, show_progress_bar=True, batch_size=256)
    embeddings = np.array(embeddings).astype('float32')
    
    dimension = embeddings.shape[1]
    print(f"Vector matrix dimension isolated: {dimension}")
    
    # Initialize a clean L2 Distance FAISS index matrix
    print("Structuring FAISS IndexFlatL2 computing layout...")
    index = faiss.IndexFlatL2(dimension)
    
    # Feed the vectorized matrices into the local memory bank
    index.add(embeddings)
    
    # Serialize and save the index file locally
    print(f"Writing trained binary array to {index_output_path}...")
    faiss.write_index(index, index_output_path)
    
    print(f"Success! FAISS vector index fully baked with {index.ntotal} items.")

if __name__ == "__main__":
    generate_production_vector_space()