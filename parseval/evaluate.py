from .evaluation.chunk_matching import ChunkEvaluator
from .schemas import GroundTruth, Predictions,  ChunkEvaluation
from typing import Literal, Tuple, Dict, List
import srsly
import os
from tqdm import tqdm


class EvaluateParser:
    """
    A class to evaluate the performance of the parser.
    """
    
    def __init__(self, method: Literal['embedding', 'lcs', 'rougeL']):
        """
        Args:
            method (str): The method to use for evaluation.
        """
        self.evaluator = ChunkEvaluator(method)


    def _get_chunk_scores(self, ground_truth_text: str, parsed_document: str, **kwargs) -> Tuple[List[str], List[float]]:
        """
        """

        return self.evaluator.compare_chunk(
            ground_truth_text, 
            parsed_document,
            **kwargs
            )

    def binary_evaluate(self, ground_truth_text: str, parsed_document: str, threshold: float = 0.8, **kwargs) -> ChunkEvaluation:
        """
        Evaluates the performance of the parser. Returns True if the best chunk has a score above the threshold, False otherwise.

        Args:
            ground_truth_chunk (str): The ground truth chunk.
            parsed_document (str): The parsed document.
            threshold (float): The threshold for a positive match.

        Returns:
            dict: A dictionary containing the best chunk, its rank, the matching score, and a boolean indicating a match.
        """

        chunks, scores = self._get_chunk_scores(ground_truth_text, parsed_document, **kwargs)
        binary_scores = [True if score >= threshold else False for score in scores]

        return ChunkEvaluation(
            chunks=chunks,
            scores=scores,
            binary_scores=binary_scores
        )





class ParserMetrics:
    parser_evaluator: EvaluateParser
    eval_scores: List[Dict]

    def __init__(
            self,
            method: Literal['embedding', 'lcs', 'rougeL']
    ):
        
        self.parser_evaluator = EvaluateParser(method=method)
        self.eval_scores = []

    def evaluate_text(self, ground_truth: GroundTruth, parser_output: Predictions, **kwargs) -> None:
        """
        Evaluate the retrieval performance for the RAG system.
        """
        try:
            for  html_path, gt_text, pred in tqdm(zip(ground_truth.html_paths, ground_truth.html_contents, parser_output.predictions), desc="Evaluating Parser", total=len(ground_truth.html_paths)):

                

                pred_text = pred.text

                chunk_eval = self.parser_evaluator.binary_evaluate(
                    ground_truth_text=gt_text,
                    parsed_document=pred_text,
                    **kwargs
                )

                matches = sum(chunk_eval.binary_scores)
                recall = matches / len(chunk_eval.binary_scores)

                average_score = sum(chunk_eval.scores) / len(chunk_eval.scores)
                min_score = min(chunk_eval.scores)
                min_score_chunk = chunk_eval.chunks[chunk_eval.scores.index(min_score)]

                max_score = max(chunk_eval.scores)
                max_score_chunk = chunk_eval.chunks[chunk_eval.scores.index(max_score)]
                
                self.eval_scores += [{
                    "file_path": html_path,
                    "num_chunks": len(chunk_eval.chunks),
                    "matches": matches,
                    "average_score": average_score,
                    "min_score": min_score,
                    "max_score": max_score,
                    "min_score_chunk": min_score_chunk,
                    "max_score_chunk": max_score_chunk,
                    "recall": recall
                }]


        except ZeroDivisionError as e:
            raise ZeroDivisionError("No chunks found in the ground truth text.") from e

    def aggregate_text_evaluation(self) -> Dict:
        """
        Aggregate the evaluation metrics (reciprocal recall and average recall) per filename.
        """
        if len(self.eval_scores) == 0:
            raise ValueError("No evaluation scores found.")
        
       
        aggregation = {
            "total_chunks": sum([score["num_chunks"] for score in self.eval_scores]),
            "total_matches": sum([score["matches"] for score in self.eval_scores]),
            "Average Recall": sum([score["recall"] for score in self.eval_scores]) / len(self.eval_scores),
            "min_recall": min([score["recall"] for score in self.eval_scores]),
            "max_recall": max([score["recall"] for score in self.eval_scores]),
            "Average Score": sum([score["average_score"] for score in self.eval_scores]) / len(self.eval_scores),
            "min_score": min([score["min_score"] for score in self.eval_scores]),
            "max_score": max([score["max_score"] for score in self.eval_scores]),
            "min_score_file": self.eval_scores[[score["min_score"] for score in self.eval_scores].index(min([score["min_score"] for score in self.eval_scores]))]["file_path"],
            "max_score_file": self.eval_scores[[score["max_score"] for score in self.eval_scores].index(max([score["max_score"] for score in self.eval_scores]))]["file_path"]
        }

        return aggregation


    def save_evaluation(self, root_dir: str):
        """
        Save the evaluation results to a JSON file.
        """
        os.makedirs(root_dir, exist_ok=True)

        if len(self.eval_scores) == 0:
            raise ValueError("No evaluation scores found.")

        srsly.write_json(os.path.join(root_dir, "parse_eval_results.json"), self.eval_scores)


    def save_aggregation(self, root_dir: str):
        """
        Save the aggregated evaluation results to a JSON file.
        """
        os.makedirs(root_dir, exist_ok=True)
        
        if len(self.eval_scores) == 0:
            raise ValueError("No evaluation scores found.")

        srsly.write_json(
            os.path.join(root_dir, "parse_aggregated_results.json"),
            self.aggregate_text_evaluation()
        )
