from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import os
from dotenv import load_dotenv

load_dotenv()

class EmbeddingService:
    def __init__(self):
        model_path = os.getenv("EMBEDDING_MODEL", "embeddingmodel/minilm")
        self.model = SentenceTransformer(model_path)

    def generate_embedding(self, cleaned_text: str):
        embedding = self.model.encode(cleaned_text)
        embedding = np.array([embedding], dtype="float32")
        faiss.normalize_L2(embedding)
        print("\n================ EMBEDDING GENERATED ================\n")
        print("Embedding Length:", len(embedding[0]))
        print("First 10 Values:", embedding[0][:10])
        print("\n=====================================================\n")
        return embedding[0].tolist()