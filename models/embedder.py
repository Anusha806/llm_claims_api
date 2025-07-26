from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')

def get_embedding(text: str):
    try:
        vec = model.encode(text)
        vec = vec.flatten()
        assert vec.shape[0] == 384, f"Expected embedding of size 384, got {vec.shape[0]}"
        return vec
    except Exception as e:
        print(f"Embedding Error: {e}")
        return None
