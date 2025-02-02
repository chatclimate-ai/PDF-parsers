from .methods.lcs import LCSEvaluator
from .methods.emb_similarity import EmbeddingEvaluator
from .methods.rouge import RougeLEvaluator
import re
from typing import Generator, Literal, Tuple, List
import tqdm





class ChunkEvaluator:
    """
    Class to evaluate the performance of a parser using chunks
    """

    def __init__(self, method: Literal['embedding', 'lcs', 'rougeL'] = 'lcs'):
        if method == 'embedding':
            self.evaluator = EmbeddingEvaluator()
        elif method == 'lcs':
            self.evaluator = LCSEvaluator()
        elif method == 'rougeL':
            self.evaluator = RougeLEvaluator()
        else:
            raise ValueError("Invalid method. Choose 'embedding' or 'lcs'.")
        
    

    def _prepare_chunks(
            self,
            ground_truth_text: str, 
            markdown_text: str, 
            method: Literal["chunk_gt", "chunk_md", "chunk_both", "chunk_grid"] = "chunk_gt",
            window_size: int = 100, 
            step_size: int = 1
            ) -> Generator[Tuple[str, str], None, None]:
        
        if method == "chunk_gt":
            gt_tokens = ground_truth_text.split()

            for start_token_idx, end_token_idx in self._sliding_window(ground_truth_text, window_size, step_size):
                gt_chunk = " ".join(gt_tokens[start_token_idx:end_token_idx])
                yield gt_chunk, markdown_text

        elif method == "chunk_md":
            md_tokens = markdown_text.split()

            for start_token_idx, end_token_idx in self._sliding_window(markdown_text, window_size, step_size):
                md_chunk = " ".join(md_tokens[start_token_idx:end_token_idx])
                yield ground_truth_text, md_chunk
        
        elif method == "chunk_both":
            gt_tokens = ground_truth_text.split()
            md_tokens = markdown_text.split()

            for start_token_idx, end_token_idx in self._sliding_window(ground_truth_text, window_size, step_size):
                gt_chunk = " ".join(gt_tokens[start_token_idx:end_token_idx])
                md_chunk = " ".join(md_tokens[start_token_idx:end_token_idx])
                yield gt_chunk, md_chunk
        
        elif method == "chunk_grid":
            gt_tokens = ground_truth_text.split()
            md_tokens = markdown_text.split()

            for start_token_idx, end_token_idx in self._sliding_window(ground_truth_text, window_size, step_size):
                for start_token_idx2, end_token_idx2 in self._sliding_window(markdown_text, window_size, step_size):

                    gt_chunk = " ".join(gt_tokens[start_token_idx:end_token_idx])
                    md_chunk = " ".join(md_tokens[start_token_idx2:end_token_idx2])
                    yield gt_chunk, md_chunk
        
        else:
            raise ValueError("Invalid method. Choose 'chunk_gt', 'chunk_md', 'chunk_both', or 'chunk_grid'.")

    
    def _total_windows_count(
            self,
            ground_truth_text: str,
            markdown_text: str,
            method: Literal["chunk_gt", "chunk_md", "chunk_both", "chunk_grid"] = "chunk_gt",
            window_size: int = 100,
            step_size: int = 1
            ):
        
        if method == "chunk_gt" or method == "chunk_both":
            gt_tokens = ground_truth_text.split()
            return (len(gt_tokens) - window_size) // step_size + 1
        
        elif method == "chunk_md":
            md_tokens = markdown_text.split()
            return (len(md_tokens) - window_size) // step_size + 1
        
        elif method == "chunk_grid":
            return self._total_windows_count(ground_truth_text, markdown_text, "chunk_gt", window_size, step_size) * self._total_windows_count(ground_truth_text, markdown_text, "chunk_md", window_size, step_size)

        else:
            raise ValueError("Invalid method. Choose 'chunk_gt', 'chunk_md', 'chunk_both', or 'chunk_grid'.")

    def compare_chunk(
            self, 
            ground_truth_text: str, 
            markdown_text: str,
            method: Literal["chunk_gt", "chunk_md", "chunk_both", "chunk_grid"] = "chunk_gt",
            window_size: int = 100,
            step_size: int=1,
            preprocess = True
            ) -> Tuple[List[str], List[float]]:
        """
        Compares the ground truth text with the markdown text using a sliding window approach.

        Args:
            ground_truth_text (str): The ground truth text.
            markdown_text (str): The markdown text.
            window_size (int): The size of the sliding window.
            step_size (int): The step size for the sliding window.

        Returns:
            tuple: A list of similarity scores and a list of corresponding chunks.

        Example:
            >>> evaluator = ChunkEvaluator('lcs')
            >>> scores, chunks = evaluator.compare_chunk(ground_truth_text, markdown_text, window_size=100, step_size=10)
            >>> print(scores)
            [0.8, 0.9, 0.7, 0.6, 0.5]
            >>> print(chunks)
            [('chunk1', 'chunk1'), ('chunk2', 'chunk2'), ('chunk3', 'chunk3'), ('chunk4', 'chunk4'), ('chunk5', 'chunk5')]
        """
        if preprocess:
            ground_truth_text = self._preprocess_text(ground_truth_text)
            markdown_text = self._preprocess_text(markdown_text)

        scores: List[float] = []
        chunks: List[str] = []

        total_windows = self._total_windows_count(ground_truth_text, markdown_text, method, window_size, step_size)
        best_score = 0

        with tqdm.tqdm(total=total_windows, desc=f"Progress (Best Score: {best_score:.4f})") as pbar:
            for gt_chunk, md_chunk in self._prepare_chunks(ground_truth_text, markdown_text, method, window_size, step_size):

                if gt_chunk == "" or md_chunk == "":
                    continue

                score = self.get_score(gt_chunk, md_chunk, preprocess = False)
                scores.append(score)
                chunks.append(gt_chunk)

                if score > best_score:
                    best_score = score

                pbar.set_description(f"Progress (Best Score: {best_score:.4f})")
                pbar.update(1)

        return chunks, scores
    
    @staticmethod
    def _sliding_window(text: str, window_size: int, step_size: int=1) -> Generator[Tuple[int, int], None, None]:
        # Generate sliding windows from the text
        tokens = text.split()  # Simple whitespace tokenization
        for i in range(0, len(tokens) - window_size + 1, step_size):
            yield (i, i + window_size)


    @staticmethod
    def _preprocess_text(text: str) -> str:
        # Clean and normalize text
        text = text.lower()

        # Remove punctuation
        text = re.sub(r'[^\w\s]', '', text)
        # remove extra white space. Leave only one space between words
        text = re.sub(r'\s+', ' ', text)

        # remove image placeholders
        text = re.sub(r"<!-- image -->", "", text)

        return text



    def get_score(self, text1: str, text2: str, preprocess = True):
        """
        Returns the similarity score between two texts.

        Args:
            text1 (str): The first text input.
            text2 (str): The second text input.
        
        Returns:
            float: The similarity score between the two texts.
        """
        if preprocess:
            text1 = self._preprocess_text(text1)
            text2 = self._preprocess_text(text2)
        return self.evaluator.similarity_score(text1, text2)
    


    def unique_words(self, text1: str, text2: str, preprocess = True):
        """
        Extracts words that are unique to text1 and text2.

        Args:
            text1 (str): The first text input.
            text2 (str): The second text input.

        Returns:
            tuple: Two lists containing words unique to text1 and text2 respectively.
        """
        if preprocess:
            text1 = self._preprocess_text(text1)
            text2 = self._preprocess_text(text2)

        set1 = set(text1.split())
        set2 = set(text2.split())

        unique_to_text1 = list(set1 - set2)
        unique_to_text2 = list(set2 - set1)

        return unique_to_text1, unique_to_text2


    def missing_words(self, ground_truth: str, markdown_text: str, preprocess = True):
        """
        Extracts the indices in text1 and text2 where words did not contribute to the LCS.
        
        Args:
            text1 (str): The first text input.
            text2 (str): The second text input.
            
        Returns:
            tuple: Two lists containing the indices of words that were skipped in text1 and text2 respectively.
        """
        if preprocess:
            text1 = self._preprocess_text(ground_truth)
            text2 = self._preprocess_text(markdown_text)

        else:
            text1 = ground_truth
            text2 = markdown_text
        
        text1 = text1.split()
        text2 = text2.split()

        # Calculate the LCS matrix
        m, n = len(text1), len(text2)
        L = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if text1[i - 1] == text2[j - 1]:
                    L[i][j] = L[i - 1][j - 1] + 1
                else:
                    L[i][j] = max(L[i - 1][j], L[i][j - 1])

        # Backtrack to find the LCS and track skipped indices in both text1 and text2
        skipped_indices_in_text1 = []
        skipped_indices_before_lcs_in_text2 = []
        skipped_indices_within_lcs_in_text2 = []
        skipped_indices_after_lcs_in_text2 = []
        
        i, j = m, n
        found_lcs = False
        while i > 0 and j > 0:
            if text1[i - 1] == text2[j - 1]:
                i -= 1
                j -= 1
                found_lcs = True
            elif L[i - 1][j] >= L[i][j - 1]:
                # Moving up: skip a word in text1
                skipped_indices_in_text1.append(i - 1)
                i -= 1
            else:
                # Moving left: skip a word in text2
                if not found_lcs:
                    # This is before the LCS starts
                    skipped_indices_before_lcs_in_text2.append(j - 1)
                else:
                    # This is within the LCS
                    skipped_indices_within_lcs_in_text2.append(j - 1)
                j -= 1

        # Any remaining words in text2 after the LCS has ended
        while j > 0:
            if found_lcs:
                skipped_indices_after_lcs_in_text2.append(j - 1)
            else:
                skipped_indices_before_lcs_in_text2.append(j - 1)
            j -= 1

        # Any remaining words in text1 that were skipped
        while i > 0:
            skipped_indices_in_text1.append(i - 1)
            i -= 1

        # The LCS is built backwards, so we need to reverse it
        skipped_indices_in_text1.reverse()
        skipped_indices_before_lcs_in_text2.reverse()
        skipped_indices_within_lcs_in_text2.reverse()
        skipped_indices_after_lcs_in_text2.reverse()
        
        return skipped_indices_in_text1, skipped_indices_before_lcs_in_text2, skipped_indices_within_lcs_in_text2, skipped_indices_after_lcs_in_text2










if __name__ == "__main__":
    ground_truth = """The second question is I'm really glad you asked it because the companies are committed to their decarbonization goals. They're not just going to abandon them because of the case before commerce or because of slightly higher prices of let's say, everything from wind turbines or solar panels to batteries due to what's happening on the mineral side, commodity side. But what people aren't talking about is that the increase in cost of renewables is much, much less than the increase in the price of fossil fuels, all of them, whether it be coal, gas or diesel. So actually, renewables are more competitive today than ever. And in almost all cases, I can say that the energy from renewables is the cheapest energy. It's just a matter of degree, how much cheaper is it even with the increase in the cost of construction. So I'd say that the main issue is not energy, it's capacity. How to keep the lights on 24/7. And you really have 2 choices. One is to continue to run your legacy assets, whether they be gas or coal and combine it with renewables. That's what we did in Chile, the sort of Green integra or Green blend and extend or energy start. And as people go, let's say, further on this journey of decarbonization, that's why there's going to be such strong demand for energy storage, lithium ion-based energy storage. So really, to me, it's a question of supply. Can you get enough batteries to meet this? And the more batteries that become available, then you'll be able to retire fossil plants sooner. So that's, I'd say, the main thing. So you're right. But on the cost equation, renewables are more competitive than ever than before this crisis."""

    markdown = "availability of natural gas but it doesnt change our of getting rid of all coal plants by 2025 second question is im really glad you asked it because the committed to their decarbonization goals theyre not just going to abandon them because of the case before commerce or because prices of let s say everything from wind turbines or solar panels batteries due to whats happening on the mineral side commodity side people arent talking about is that the increase in cost much less than the increase in the price of fossil fuels all of them whether it be coal gas or diesel actually renewables are more competitive today than ever and cases i can say that the energy from renewables is the cheapest a matter of degree how much cheaper is it even with the cost of construction id say that the main issue is not energy its capacity how to keep on 247 and you really have 2 choices one is to continue to run assets whether they be gas or coal and combine it with what we did in chile the sort of green integra or green blend or energy start and as people go lets say further on this decarbonization thats why theres going to be such strong demand for storage lithium ionbased energy storage really to me its a question of supply can you get enough batteries this and the more batteries that become available then youll be retire fossil plants sooner thats id say the main thing youre right but on the cost equation renewables are more ever before this crisis because it is pretty amazing to see that large commercial are comfortable locking in for example in pjm power high as 50 in 2026 2027 when"

    evaluator = ChunkEvaluator('lcs')

    import time
    start = time.time()
 
    scores, chunks = evaluator.compare_chunk(ground_truth, markdown, window_size=100, step_size=10)
    best_chunks = chunks[scores.index(max(scores))]

    print("\nBest chunk:", best_chunks, "of score:", max(scores))



    skipped_indices_in_text1, skipped_indices_before_lcs_in_text2, skipped_indices_within_lcs_in_text2, skipped_indices_after_lcs_in_text2 = evaluator.missing_words(ground_truth, markdown)

    missing_in_ground_before = [markdown.split()[i] for i in skipped_indices_before_lcs_in_text2]
    print("\nMissing in ground and present in markdown after lcs:", len(missing_in_ground_before), missing_in_ground_before)

    missing_in_ground_after = [markdown.split()[i] for i in skipped_indices_after_lcs_in_text2]
    print("\nMissing in ground and present in markdown before lcs:", len(missing_in_ground_after), missing_in_ground_after)


    missing_in_ground_in = [markdown.split()[i] for i in skipped_indices_within_lcs_in_text2]
    print("\nMissing in ground and present in markdown within lcs:", len(missing_in_ground_in), missing_in_ground_in)


    missing_in_markdown = [ground_truth.split()[i] for i in skipped_indices_in_text1]
    print("\nMissing in markdown and present in ground:", len(missing_in_markdown), missing_in_markdown)

    print("Time taken:", time.time() - start)
