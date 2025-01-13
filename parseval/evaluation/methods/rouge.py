from rouge import Rouge


class RougeLEvaluator:
    def __init__(self):
        self.rouge = Rouge()

    def similarity_score(self, text1: str, text2: str) -> float:
        # Calculate the ROUGE-L score between two texts
        scores = self.rouge.get_scores(text1, text2)
        return scores[0]['rouge-l']['f']

