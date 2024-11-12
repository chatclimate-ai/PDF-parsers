from sentence_transformers import SentenceTransformer, util
from typing import List



class EmbeddingEvaluator:
    """
    Class to evaluate the performance of a parser using embeddings
    """

    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')


    def get_embeddings(self, text: str) -> List[float]:
        # Get embeddings for a given text
        return self.model.encode(text, convert_to_tensor=True)
    
    def similarity_score(self, text1: str, text2: str) -> float:
        # Calculate the cosine similarity between two texts
        embedding1 = self.get_embeddings(text1)
        embedding2 = self.get_embeddings(text2)
        return util.cos_sim(embedding1, embedding2).item()
