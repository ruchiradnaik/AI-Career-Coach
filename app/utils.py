def split_text_into_chunks(text, chunk_size=500):
    """
    Splits text into smaller chunks for embedding.
    """
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks
