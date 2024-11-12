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
