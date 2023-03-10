import unittest

try:
    from .evaluation import evaluation_function
except ImportError:
    from evaluation import evaluation_function


class TestEvaluationFunction(unittest.TestCase):
    """
        TestCase Class used to test the algorithm.
        ---
        Tests are used here to check that the algorithm written
        is working as it should. 
        
        It's best practise to write these tests first to get a
        kind of 'specification' for how your algorithm should
        work, and you should run these tests before committing
        your code to AWS.

        Read the docs on how to use unittest here:
        https://docs.python.org/3/library/unittest.html

        Use evaluation_function() to check your algorithm works
        as it should.
    """
    def test_returns_is_correct_true(self):
        response, answer, params = "A xor gate takes 2 inputs", "There are 2 inputs in a xor gate", dict()
        result = evaluation_function(response, answer, params)
        self.assertEqual(result.get("is_correct"), True)

    def test_with_keyword(self):
        response = "An undirected graph with no cycles and no double edges"
        answer = "A simple undirected acyclic graph"
        params = {"keywords": ["acyclic"]}
        result = evaluation_function(response, answer, params)
        self.assertEqual(result.get("is_correct"), True)
        self.assertEqual("INDETERMINABLE" in result[tags].keys(), True)
        self.assertEqual(result["result"]["Problematic_word"] == "acyclic")

    def test_with_problematic_word(self):
        response = "A banana of characters"
        answer = "A list of characters"
        params = dict()
        result = evaluation_function(response, answer, params)
        self.assertEqual(result.get("is_correct"), False)
        self.assertEqual("HAS_PROBLEMATIC_WORD" in result[tags].keys(), True)
        self.assertEqual(result["result"]["Problematic_word"] == "list")

if __name__ == "__main__":
    unittest.main()
