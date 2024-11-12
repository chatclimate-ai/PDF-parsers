from .evaluation.chunk_matching import ChunkEvaluator
from .schemas import GroundTruth
from typing import Literal, Tuple, Dict, List
from pathlib import Path
import srsly
import os
from tqdm import tqdm
from pandas import DataFrame


class ParserMetrics:
    """
    A class to evaluate the performance of the parser.
    """
    
    def __init__(self, method: Literal['embedding', 'lcs'], preprocess: bool = False):
        """
        Args:
            method (str): The method to use for evaluation.
            preprocess (bool): Whether to preprocess the text before evaluation.
        """
        self.evaluator = ChunkEvaluator(method, preprocess)


    def _find_most_similar_chunk(self, ground_truth_chunk: str, parsed_document: str, **kwargs) -> Tuple[str, float]:
        """
        Finds the most similar chunk to the ground truth chunk from the parsed document.

        Args:
            ground_truth_chunk (str): The ground truth chunk.
            parsed_document (str): The parsed document.

        Returns:
            str: The most similar chunk from the parsed document.
        """

        best_chunk, best_score = self.evaluator.get_most_similar_chunk(ground_truth_chunk, parsed_document, **kwargs)

        return best_chunk, best_score
    

    def evaluate(self, ground_truth_chunk: str, parsed_document: str, **kwargs) -> Dict[str, float]:
        """
        Evaluates the performance of the parser. Finds the most similar chunk to the ground truth chunk from the parsed document.

        Args:
            ground_truth_chunk (str): The ground truth chunk.
            parsed_document (str): The parsed document.

        Returns:
            dict: A dictionary containing the best chunk, its rank, and the matching score.
        """

        best_chunk, best_score = self._find_most_similar_chunk(ground_truth_chunk, parsed_document, **kwargs)

        return {
            "best_chunk": best_chunk,
            "best_score": best_score
        }
    

    def binary_evaluate(self, ground_truth_chunk: str, parsed_document: str, threshold: float = 0.8, **kwargs) -> Dict[str, float]:
        """
        Evaluates the performance of the parser. Returns True if the best chunk has a score above the threshold, False otherwise.

        Args:
            ground_truth_chunk (str): The ground truth chunk.
            parsed_document (str): The parsed document.
            threshold (float): The threshold for a positive match.

        Returns:
            dict: A dictionary containing the best chunk, its rank, the matching score, and a boolean indicating a match.
        """

        result = self.evaluate(ground_truth_chunk, parsed_document, **kwargs)

        if result["best_score"] >= threshold:
            result["match"] = True
        else:
            result["match"] = False

        return result





class EvaluateParser:
    gt_elements: List[GroundTruth] = []
    parser_metrics: ParserMetrics
    gt_scores: List[Dict] = []

    def __init__(
            self,
            gt_file_path: Path,
            method: Literal['embedding', 'lcs'],
    ):
        if not gt_file_path.exists():
            raise FileNotFoundError(f"File not found: {gt_file_path}")
        if not gt_file_path.suffix == ".json":
            raise ValueError("Ground truth file must be in JSON format.")

        self.gt_elements = [GroundTruth(**item) for item in srsly.read_json(gt_file_path)]
        self.parser_metrics = ParserMetrics(method=method, preprocess=True)

    def evaluate(self, markdown_dir: str) -> None:
        """
        Evaluate the retrieval performance for the RAG system.
        """
        try:
            for gt in tqdm(self.gt_elements, desc="Evaluating Parser", unit="gt"):
                gt_score = gt.model_dump()

                gt_score["parser_output"] = []
                markdown_path = os.path.join(markdown_dir, gt.file_name)
                with open(markdown_path, 'r') as f:
                    parsed_document = f.read()

                for evidence in gt.evidences:
                    gt_score["parser_output"] += [
                        self.parser_metrics.binary_evaluate(
                            ground_truth_chunk=evidence,
                            parsed_document=parsed_document,
                            threshold=0.8,
                            step_size = 100
                        )
                    ]

                # Calculating the recall
                matches = [i["match"] for i in gt_score["parser_output"]]
                gt_score["recall"] = sum(matches) / len(gt.evidences)

                # del gt_score["retriever_output"]
                self.gt_scores += [gt_score]

        except ZeroDivisionError as e:
            raise ZeroDivisionError("No evidence found in the ground truth file. Please check the ground truth file.") from e

    def aggregate_evaluation(self, markdown_dir: str) -> Dict:
        """
        Aggregate the evaluation metrics (reciprocal recall and average recall) per filename.
        """
        self.evaluate(markdown_dir)

        if len(self.gt_scores) == 0:
            raise ValueError("No evaluation scores found.")
        
        # transform the gt_scores into a pandas dataframe
        df = DataFrame(self.gt_scores)
        aggregation = df.groupby("file_name").agg({
            "recall": "mean"
        })

        # Rename the columns to make them more descriptive
        aggregation = aggregation.rename(columns={
            "recall": "mean_recall"
        })

        return aggregation.to_dict()


    def save_evaluate(self, root_dir: Path):
        """
        Save the evaluation results to a JSON file.
        """
        if not root_dir.exists():
            root_dir.mkdir(parents=True)

        if len(self.gt_scores) == 0:
            raise ValueError("No evaluation scores found.")

        srsly.write_json(os.path.join(root_dir, "parse_eval_results.json"), self.gt_scores)


    def save_aggregation(self, root_dir: Path):
        """
        Save the aggregated evaluation results to a JSON file.
        """
        if not root_dir.exists():
            root_dir.mkdir(parents=True)
        
        if len(self.gt_scores) == 0:
            raise ValueError("No evaluation scores found.")

        srsly.write_json(
            os.path.join(root_dir, "parse_aggregated_results.json"),
            self.aggregate_evaluation()
        )
