from typing import List

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks: List[str] = []
    step = chunk_size - overlap

    for i in range(0, len(text), step):
        chunk = text[i:i + chunk_size]
        if chunk:
            chunks.append( ''.join(chunk))
    

    return chunks
    
