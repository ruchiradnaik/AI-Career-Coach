from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

def embed_chunks(chunks):
    """
    Takes a list of text chunks and returns their vector embeddings.
    """
    embeddings = model.encode(chunks, show_progress_bar=False)
    return np.array(embeddings)

def build_faiss_index(chunks):
    """
    Creates a FAISS index from text chunks and returns the index and metadata.
    """
    embeddings = embed_chunks(chunks)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index, embeddings

def search_index(query, index, chunks, top_k=3):
    """
    Search FAISS index with a query and return top-k matching chunks.
    """
    query_embedding = model.encode([query])
    _, I = index.search(np.array(query_embedding), top_k)
    return [chunks[i] for i in I[0]]

def get_top_k_chunks(index, chunks, query, k=3):
    """
    Given a FAISS index and list of chunks, return top-k relevant chunks for a query.
    """
    query_embedding = model.encode([query])
    _, indices = index.search(query_embedding, k)
    return [chunks[i] for i in indices[0] if i < len(chunks)]

