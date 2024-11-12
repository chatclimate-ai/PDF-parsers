from sentence_transformers import SentenceTransformer, util
import re
from typing import List, Generator, Literal
import tqdm

def preprocess_text(text: str) -> str:
    # Clean and normalize text
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    # remove extra white space. Leave only one space between words
    text = re.sub(r'\s+', ' ', text)
    # text = word_tokenize(text)  # Tokenize into words
    return text


def sliding_window(text: str, window_size: int, step_size: int=1) -> Generator[str, None, None]:
    # Generate sliding windows from the text
    tokens = text.split()  # Simple whitespace tokenization
    for i in range(0, len(tokens) - window_size + 1, step_size):
        yield ' '.join(tokens[i:i + window_size])





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
    


class LCSEvaluator:
    """
    Class to evaluate the performance of a parser using the longest common subsequence
    """

    def __init__(self):
        pass

    def similarity_score(self, text1: str, text2: str):
        # Calculate the length of the longest common subsequence
        text1 = text1.split()
        text2 = text2.split()

        m, n = len(text1), len(text2)
        L = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(m + 1):
            for j in range(n + 1):
                if i == 0 or j == 0:
                    L[i][j] = 0
                elif text1[i - 1] == text2[j - 1]:
                    L[i][j] = L[i - 1][j - 1] + 1
                else:
                    L[i][j] = max(L[i - 1][j], L[i][j - 1])
                    
        return L[m][n] / m


    


class ChunkEvaluator:
    """
    Class to evaluate the performance of a parser using chunks
    """

    def __init__(self, method: Literal['embedding', 'lcs'], preprocess = True):
        if method == 'embedding':
            self.evaluator = EmbeddingEvaluator()
        elif method == 'lcs':
            self.evaluator = LCSEvaluator()
        else:
            raise ValueError("Invalid method. Choose 'embedding' or 'lcs'.")
        
        self.preprocess = preprocess


    def get_most_similar_chunk(self, ground_truth_text: str, markdown_text: str, step_size: int=1):
        # Find the most similar chunk in the markdown text
        if self.preprocess:
            ground_truth_text = preprocess_text(ground_truth_text)
            markdown_text = preprocess_text(markdown_text)

        window_size = len(ground_truth_text.split())

        best_score = 0
        best_chunk = ""

        markdown_tokens = markdown_text.split()
        total_windows = (len(markdown_tokens) - window_size) // step_size + 1

        with tqdm.tqdm(total=total_windows, desc=f"Sliding Window Progress (Best Score: {best_score:.4f})") as pbar:
            for window_text in sliding_window(markdown_text, window_size, step_size):
                score = self.evaluator.similarity_score(ground_truth_text, window_text)

                if score > best_score:
                    best_score = score
                    best_chunk = window_text
              
                pbar.set_description(f"Sliding Window Progress (Best Score: {best_score:.4f})")
                pbar.update(1)
        
        return best_chunk, best_score


    def get_score(self, text1: str, text2: str):
        if self.preprocess:
            text1 = preprocess_text(text1)
            text2 = preprocess_text(text2)
        return self.evaluator.similarity_score(text1, text2)
    


    def unique_words(self, text1: str, text2: str):
        """
        Extracts words that are unique to text1 and text2.

        Args:
            text1 (str): The first text input.
            text2 (str): The second text input.

        Returns:
            tuple: Two lists containing words unique to text1 and text2 respectively.
        """
        if self.preprocess:
            text1 = preprocess_text(text1)
            text2 = preprocess_text(text2)

        set1 = set(text1.split())
        set2 = set(text2.split())

        unique_to_text1 = list(set1 - set2)
        unique_to_text2 = list(set2 - set1)

        return unique_to_text1, unique_to_text2


    def missing_words(self, ground_truth: str, markdown_text: str):
        """
        Extracts the indices in text1 and text2 where words did not contribute to the LCS.
        
        Args:
            text1 (str): The first text input.
            text2 (str): The second text input.
            
        Returns:
            tuple: Two lists containing the indices of words that were skipped in text1 and text2 respectively.
        """
        if self.preprocess:
            text1 = preprocess_text(ground_truth)
            text2 = preprocess_text(markdown_text)

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
    ground_truth_chunk = """The second question is I'm really glad you asked it because the companies are committed to their decarbonization goals. They're not just going to abandon them because of the case before commerce or because of slightly higher prices of let's say, everything from wind turbines or solar panels to batteries due to what's happening on the mineral side, commodity side. But what people aren't talking about is that the increase in cost of renewables is much, much less than the increase in the price of fossil fuels, all of them, whether it be coal, gas or diesel. So actually, renewables are more competitive today than ever. And in almost all cases, I can say that the energy from renewables is the cheapest energy. It's just a matter of degree, how much cheaper is it even with the increase in the cost of construction. So I'd say that the main issue is not energy, it's capacity. How to keep the lights on 24/7. And you really have 2 choices. One is to continue to run your legacy assets, whether they be gas or coal and combine it with renewables. That's what we did in Chile, the sort of Green integra or Green blend and extend or energy start. And as people go, let's say, further on this journey of decarbonization, that's why there's going to be such strong demand for energy storage, lithium ion-based energy storage. So really, to me, it's a question of supply. Can you get enough batteries to meet this? And the more batteries that become available, then you'll be able to retire fossil plants sooner. So that's, I'd say, the main thing. So you're right. But on the cost equation, renewables are more competitive than ever than before this crisis."""

    evaluator = ChunkEvaluator('lcs', preprocess=True)

    # with open("data/Goku/test_parsed/-001-021-AES_Q12022_earningscall_6.5.22_july2022.pdf.md", "r") as file:
    #     markdown_text = file.read()

    import time

    start = time.time()
    # best_chunk, score = evaluator.get_most_similar_chunk(
    #     ground_truth_chunk, 
    #     markdown_text,
    #     step_size=100)
    
    # print(f"Best chunk: {best_chunk}", f"Score: {score}", sep="\n")
    # print("Time taken:", time.time() - start)

    # # test
    # print(evaluator.get_score(ground_truth_chunk, best_chunk) == score)

    best_chunk = "availability of natural gas but it doesnt change our of getting rid of all coal plants by 2025 second question is im really glad you asked it because the committed to their decarbonization goals theyre not just going to abandon them because of the case before commerce or because prices of let s say everything from wind turbines or solar panels batteries due to whats happening on the mineral side commodity side people arent talking about is that the increase in cost much less than the increase in the price of fossil fuels all of them whether it be coal gas or diesel actually renewables are more competitive today than ever and cases i can say that the energy from renewables is the cheapest a matter of degree how much cheaper is it even with the cost of construction id say that the main issue is not energy its capacity how to keep on 247 and you really have 2 choices one is to continue to run assets whether they be gas or coal and combine it with what we did in chile the sort of green integra or green blend or energy start and as people go lets say further on this decarbonization thats why theres going to be such strong demand for storage lithium ionbased energy storage really to me its a question of supply can you get enough batteries this and the more batteries that become available then youll be retire fossil plants sooner thats id say the main thing youre right but on the cost equation renewables are more ever before this crisis because it is pretty amazing to see that large commercial are comfortable locking in for example in pjm power high as 50 in 2026 2027 when"


    skipped_indices_in_text1, skipped_indices_before_lcs_in_text2, skipped_indices_within_lcs_in_text2, skipped_indices_after_lcs_in_text2 = evaluator.missing_words(ground_truth_chunk, best_chunk)

    missing_in_ground_before = [best_chunk.split()[i] for i in skipped_indices_before_lcs_in_text2]
    print("\nMissing in ground and present in markdown after lcs:", len(missing_in_ground_before), missing_in_ground_before)

    missing_in_ground_after = [best_chunk.split()[i] for i in skipped_indices_after_lcs_in_text2]
    print("\nMissing in ground and present in markdown before lcs:", len(missing_in_ground_after), missing_in_ground_after)


    missing_in_ground_in = [best_chunk.split()[i] for i in skipped_indices_within_lcs_in_text2]
    print("\nMissing in ground and present in markdown within lcs:", len(missing_in_ground_in), missing_in_ground_in)


    missing_in_markdown = [ground_truth_chunk.split()[i] for i in skipped_indices_in_text1]
    print("\nMissing in markdown and present in ground:", len(missing_in_markdown), missing_in_markdown)

    print("Time taken:", time.time() - start)
