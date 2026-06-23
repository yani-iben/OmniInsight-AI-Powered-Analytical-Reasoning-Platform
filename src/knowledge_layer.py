import os
import faiss
from sentence_transformers import SentenceTransformer
import numpy as np

def build_vector_knowledge_base(memo_path="data/operational_memos.txt", index_path="data/knowledge_layer.index"):
    encoder=SentenceTransformer('all-MiniLM-L6-v2')
    embedding_dim=384

    if not os.path.exists(memo_path):
        raise FileNotFoundError(f"Missing unstructured data file at {memo_path}. Please run generate_data.py first!")
    
    with open(memo_path, "r") as f:
        raw_content=f.read()

    documents= [doc.strip() for doc in raw_content.split("=== DOCUMENT BREAK ===") if doc.strip()]

    print("⚡ Vectorizing text blocks into 384-dimensional dense arrays...")
    embeddings = encoder.encode(documents, show_progress_bar=False)
    embeddings_matrix = np.array(embeddings).astype('float32')

    # Instantiate and Populate the FAISS Index
    # IndexFlatL2 performs an exact Euclidean distance metric search over the matrix
    index = faiss.IndexFlatL2(embedding_dim)
    index.add(embeddings_matrix)

    faiss.write_index(index, index_path)

    # Build an In-Memory Lookup Map for Text Retrieval
    # Because FAISS only stores numerical vectors, we must map index IDs back to text strings
    with open("data/document_map.txt", "w") as f:
        for doc in documents:
            f.write(doc.replace("\n", " ") + "\n")
    return encoder, index, documents

def execute_semantic_search(user_query, k=1):
    """Simple test function to prove the search works"""
    #HuggingFace's SentenceTransformer model for encoding text into dense vectors
    encoder=SentenceTransformer('all-MiniLM-L6-v2')

    #Load the FAISS Index
    index=faiss.read_index("data/knowledge_layer.index")

    with open("data/document_map.txt", "r") as f:
        documents= f.readlines()

    query_vector=encoder.encode([user_query]).astype('float32')
    #calculate euclidean distance to find top K nearest vectors
    distances, indices=index.search(query_vector, k)

    print(f"\nSEMANTIC RETRIEVAL TESTING FOR QUERY: '{user_query}'")
    for dist, idx in zip(distances[0], indices[0]):
        if idx != -1:
            print(f"Match Found (Distance Error Score: {dist:.4f}):")
            print(f"   {documents[idx].strip()}\n")
if __name__ == "__main__":
    build_vector_knowledge_base()
    execute_semantic_search("Are there any administrative resource challenges during weekends?")